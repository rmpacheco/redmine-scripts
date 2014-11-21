import requests
import json
import csv
from redmine import *
from dateutil import rrule
from datetime import date, datetime, timedelta
import sys
import getopt

def workdays(start, end, holidays=0, days_off=None):
    if days_off is None:
        days_off = 5, 6         # default to: saturdays and sundays
    workdays = [x for x in range(7) if x not in days_off]
    days = rrule.rrule(rrule.DAILY, dtstart=start, until=end,
                       byweekday=workdays)
    return days.count( ) - holidays
print "hello"

# read our access key
f = open('key.txt', 'r')
accessKey = f.read()
f.close()

# read our sprint data
rows = []
with open('C:\\Users\\roman\\Box Sync\\Team Sprint Performance Reports\\sprint_calc_data.csv', 'rb') as csvfile:
    dataReader = csv.reader(csvfile, delimiter=',', quotechar='"')
    i = 0
    for row in dataReader:
        i+=1
        # skip header row
        if i == 1:continue
        rows.append(row)

# aggregate all sprint data by dev
sprintsByDev = {"Bentley":{}, "Isaac":{}, "Gordon":{}, "Ryan":{}, "Roman":{}}
for row in rows:
    nextOffset = 0
    total_count=1
    total_sp = 0.0
    total_worked = 0.0
    issues = []
    while nextOffset < total_count:
        uri = 'https://redmine1h.gdsx.com/redmine/projects/tla/issues.json?set_filter=1&f%5B%5D=fixed_version_id&op%5Bfixed_version_id%5D=%3D&v%5Bfixed_version_id%5D%5B%5D=' + row[1] + '&f%5B%5D=tracker_id&op%5Btracker_id%5D=%3D&v%5Btracker_id%5D%5B%5D=6&v%5Btracker_id%5D%5B%5D=12&v%5Btracker_id%5D%5B%5D=13&v%5Btracker_id%5D%5B%5D=14&v%5Btracker_id%5D%5B%5D=15&v%5Btracker_id%5D%5B%5D=17&f%5B%5D=status_id&op%5Bstatus_id%5D=%21&v%5Bstatus_id%5D%5B%5D=6&v%5Bstatus_id%5D%5B%5D=22&f%5B%5D=&c%5B%5D=tracker&c%5B%5D=category&c%5B%5D=status&c%5B%5D=priority&c%5B%5D=subject&c%5B%5D=done_ratio&c%5B%5D=cf_9&c%5B%5D=cf_17&group_by=&limit=100&offset=' + str(nextOffset)
        r = requests.get(uri, params={'key': accessKey}, verify=False)
        data = json.loads(r.text)
        total_count = data["total_count"]
        setSize =len(data["issues"])
        for x in xrange (0, setSize):
            issue = RmIssue(data["issues"][x])
            issues.append(issue)
            done= issue.done_ratio
            # get story points estimate for the issue
            total_sp += issue.estimated_sp
            total_worked += issue.worked_sp
        
        nextOffset += setSize
    
    numBDaysInSprint = 10 #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    # define number of business hours in this sprint
    bus_hours_per_sprint = 75  # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    time_entries = []

    #TODO: input the dev information from a file, including time off data for each sprint
    devs = {237:Dev(237, "Bentley", int(row[6])), 212: Dev(212, "Isaac",int(row[5])), 128: Dev(128, "Gordon",int(row[2])), 12:Dev(12, "Ryan",int(row[3])), 15: Dev(15, "Roman",int(row[4]))}
    for i in issues:
        # prime the list of dev hours for this issue
        devHoursForIssue = {}
        for d in devs:
            devHoursForIssue[d] = 0

        total_hours_for_issue = 0

        # get time entries
        r = requests.get('https://redmine1h.gdsx.com/redmine/issues/%d/time_entries.json?limit=50' % (i.id), params={'key': accessKey}, verify=False)
        data = json.loads(r.text)
        for x in xrange (0, data["total_count"]):
            entry = TimeEntry(data["time_entries"][x])
            devHoursForIssue[entry.user_id] += entry.hours
            total_hours_for_issue += entry.hours
        keys = devHoursForIssue.keys()
        if total_hours_for_issue > 0:
            for y in xrange(0, len(keys)):
                devPercByHours = devHoursForIssue[keys[y]] / total_hours_for_issue
                devs[keys[y]].totalSpWorked += i.worked_sp * devPercByHours
                devs[keys[y]].adjustedTotalSpWorked += i.adjusted_worked_sp * devPercByHours
                devs[keys[y]].totalHoursWorked+=devHoursForIssue[keys[y]]          
    sprintNum = int(row[0])
    print "Sprint %d: %d story points" % (sprintNum, total_sp)
    sprintsByDev["Bentley"][sprintNum] = devs[237]
    sprintsByDev["Isaac"][sprintNum] = devs[212]
    sprintsByDev["Gordon"][sprintNum] = devs[128]
    sprintsByDev["Ryan"][sprintNum] = devs[12]
    sprintsByDev["Roman"][sprintNum] = devs[15]
    total_projected_sp = 0

    #print "\ndev\t\thrs logged\ttotal sp impact (adj)\tave sp / hr logged\tave sp / bus hr (day)"
    #print "------------------------------------------------------------------------------------------------------"
    #for dkey in devs.keys():
    #    dev = devs[dkey]
    #    dev.busDayEfficiency = (dev.totalSpWorked/(bus_hours_per_sprint-(8*dev.daysOff)))
    #    #print "%10s:\t%.2f hrs on stories,\t%.2f (%.2f) story points impacted,\tave. sp / hr logged: %.2f,\tave. sp / bus. hr: %.2f (%.2f)" % (dev.name, dev.totalHoursWorked, dev.totalSpWorked, dev.adjustedTotalSpWorked, dev.hourEfficiency(), dev.busDayEfficiency, dev.busDayEfficiency * 8)
    #    print "%s\t\t%.2f\t\t%.2f (%.2f)\t\t%10.2f\t\t%.2f (%.2f)" % (dev.name, dev.totalHoursWorked, dev.totalSpWorked, dev.adjustedTotalSpWorked, dev.hourEfficiency(), dev.busDayEfficiency, dev.busDayEfficiency * 8)
    #print "\n\n\n"

# print out sprint info by dev


if len(sys.argv) > 1:
    opts, args = getopt.getopt(sys.argv[1:],"c")
    for opt, arg in opts:
      if opt == '-c':
         for devKey in sorted(sprintsByDev.keys()):
            print str(devKey)
            #print "\nsprint\t\thrs logged\ttotal sp impact (adj)\tave sp per hr logged / bus hour / bus day"
            print "------------------------------------------------------------------------------------------------------"
            for sprintKey in  sorted(sprintsByDev[devKey].keys()):
                dev = sprintsByDev[devKey][sprintKey]
                dev.busDayEfficiency = (dev.totalSpWorked/(bus_hours_per_sprint-(8*dev.daysOff)))
                print "%.2f\t%.2f\t%.2f\t\t%.2f\t%.2f\t\t%.2f" % (dev.totalHoursWorked, dev.totalSpWorked, dev.adjustedTotalSpWorked, dev.hourEfficiency(), dev.busDayEfficiency, dev.busDayEfficiency * 8)
            print "\n\n"
else:
    for devKey in sorted(sprintsByDev.keys()):
        print str(devKey)
        print "\nsprint\t\thrs logged\ttotal sp impact (adj)\tave sp per hr logged / bus hour / bus hour (adj)"
        print "------------------------------------------------------------------------------------------------------"
        for sprintKey in  sorted(sprintsByDev[devKey].keys()):
            dev = sprintsByDev[devKey][sprintKey]
            dev.busDayEfficiency = (dev.adjustedTotalSpWorked/(bus_hours_per_sprint-(8*dev.daysOff)))
            print "%s\t\t%.2f\t\t%.2f (%.2f)\t%10.2f / %.2f / %.2f" % (sprintKey, dev.totalHoursWorked, dev.totalSpWorked, dev.adjustedTotalSpWorked, dev.hourEfficiency(), dev.busDayEfficiency, dev.adjustedBusDayEfficiency)
        print "\n\n"