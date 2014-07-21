import requests
import json
from redmine import *
from dateutil import rrule
from datetime import date, datetime, timedelta
from colorama import init
from colorama import Fore, Back, Style
init() #init colorama

def workdays(start, end, holidays=0, days_off=None):
    if days_off is None:
        days_off = 5, 6         # default to: saturdays and sundays
    workdays = [x for x in range(7) if x not in days_off]
    days = rrule.rrule(rrule.DAILY, dtstart=start, until=end,
                       byweekday=workdays)
    return days.count( ) - holidays


nextOffset = 0
total_count=1
total_sp = 0.0
total_worked = 0.0
issues = []
while nextOffset < total_count:
    #print "nextOffset = %d, total_count = %d" % (nextOffset, total_count)
    uri = 'https://redmine1h.gdsx.com/redmine/projects/tla/issues.json?query_id=214&limit=100&offset=' + str(nextOffset)
    #uri = 'https://redmine1h.gdsx.com/redmine/time_entries.json?utf8=%E2%9C%93&f%5B%5D=spent_on&op%5Bspent_on%5D=lm&limit=100&offset=' + str(nextOffset)
    # TODO: have the user input their user name and password)
    r = requests.get(uri, auth=('roman', ''), verify=False)
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
        
        #print "story: %d, points: %d, done percentage: %f" % (issue.id, issue.estimated_sp, issue.done_ratio)
    nextOffset += setSize
print "total story points to be worked: %d" % (total_sp)
print "total story points worked so far: %.2f" % (total_worked)
perc_completed_to_date = float(100) * (total_worked / total_sp)
print "percentage of sprint completed so far: %.2f%%" % (perc_completed_to_date)

numBDaysInSprint = 10 #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# determine the sprint start date
# TODO: make this a command line arg (or better yet, make it come from redmine)
sprint_start_date = date(2014,7,7)  # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# define number of business hours in this sprint
bus_hours_per_sprint = 75  # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# determine number of business hours transpired
wd = workdays(sprint_start_date, date.today())
if wd < numBDaysInSprint:
    bus_hours = wd * 8
else:
    bus_hours= bus_hours_per_sprint

targeted_perc_for_parity = (float(bus_hours) / bus_hours_per_sprint) * 100
print "business hours as of end of today: %d" % (bus_hours)
print "targed sprint progress for parity: %.2f%%" % (targeted_perc_for_parity)

story_points_behind =  0
if (targeted_perc_for_parity > perc_completed_to_date):
    story_points_behind = (.01) * (targeted_perc_for_parity - perc_completed_to_date) * total_sp
print "story points to complete today for parity: %.2f" % (story_points_behind)

time_entries = []
bentley = Dev(237, "Bentley")
isaac = Dev(212, "Isaac")
gordon = Dev(128, "Gordon")
ryan = Dev(12, "Ryan")
roman = Dev(15, "Roman")

devs = {237:bentley, 212:isaac, 128:gordon, 12:ryan, 15:roman}
#devNames = {237:"Bentley", 212:"Isaac", 128: "Gordon", 12: "Ryan", 15: "Roman"}
#devSpForSprint = {237:0, 212:0, 128:0, 12:0, 15:0}
for i in issues:
    #print "story %d" % i.id
    devHoursForIssue = {237:0, 212:0, 128:0, 12:0, 15:0}
    total_hours_for_issue = 0
    # get time entries
    r = requests.get('https://redmine1h.gdsx.com/redmine/issues/%d/time_entries.json?limit=50' % (i.id), auth=('roman', ''), verify=False)
    data = json.loads(r.text)
    for x in xrange (0, data["total_count"]):
        entry = TimeEntry(data["time_entries"][x])
        devHoursForIssue[entry.user_id] += entry.hours
        total_hours_for_issue += entry.hours
    keys = devHoursForIssue.keys()
    #print devHoursForIssue
    if total_hours_for_issue > 0:
        for y in xrange(0, len(keys)):
            devPercByHours = devHoursForIssue[keys[y]] / total_hours_for_issue
            devs[keys[y]].totalSpWorked += i.worked_sp * devPercByHours
            devs[keys[y]].adjustedTotalSpWorked += i.adjusted_worked_sp * devPercByHours
            devs[keys[y]].totalHoursWorked+=devHoursForIssue[keys[y]]
    else:
        if i.worked_sp > 0:
            print (Back.YELLOW + Fore.BLACK + "Warning: Story %d claims progress but has 0 spent time recorded" % (i.id) + Back.RESET + Fore.RESET)          

for dkey in devs.keys():
    dev = devs[dkey]
    
    #print "%10s:\t%.2f hrs on stories,\t%.2f story points impacted,\tave. sp / hour: %.2f " % (dev.name, dev.totalHoursWorked, dev.totalSpWorked, dev.hourEfficiency())
    print "%10s:\t%.2f hrs on stories,\t%.2f (%.2f) story points impacted,\tave. sp / hour: %.2f" % (dev.name, dev.totalHoursWorked, dev.totalSpWorked, dev.adjustedTotalSpWorked, dev.hourEfficiency())

