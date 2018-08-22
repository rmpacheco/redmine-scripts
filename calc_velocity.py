import json
import sys

import requests

from redmine import *

requests.packages.urllib3.disable_warnings()

def workdays(start, end, holidays=0, days_off=None):
    if days_off is None:
        days_off = 5, 6  # default to: saturdays and sundays
    workdays = [x for x in range(7) if x not in days_off]
    days = rrule.rrule(rrule.DAILY, dtstart=start, until=end,
                       byweekday=workdays)
    return days.count() - holidays 


def addDevStatsRow(title, devs, attr):
    row = title + (" " * (14 - len(title))) + "|"
    for dkey in devs.keys():
        dev = devs[dkey]
        row += ("%15s" % ("%.2f" % getattr(dev, attr)))
    return row

def getDayFactor(dev):
    dayFactor = 8
    # if dev == mosley:
    #     dayFactor = 4
    return dayFactor

def hoursToSP(hours):
    return hours*team_efficiency_index

class RmStory(object):
    def __init__(self, issue):
        self.id = issue.id
        self.subject = issue.subject
        self.estimated_sp = issue.estimated_sp
        self.worked_sp = issue.worked_sp
        self.remaining_sp = issue.estimated_sp - issue.worked_sp
        self.estimated_hours = issue.estimated_hours
        self.spent_hours = 0
        self.status_name = issue.status_name
        self.status = issue.status
    def getRemainingHours(self):
        return self.estimated_hours - self.spent_hours

if len(sys.argv) <= 1:
    print "Sprint ID required as command line arg"
else:

    # read our access key
    
    accessKey = "yourkey" 
    

    version = sys.argv[1]

    nextOffset = 0
    total_count = 1
    stories = {}
    issues = []
    while nextOffset < total_count:
        uri = 'https://redmine1h.gdsx.com/redmine/projects/tla/issues.json?set_filter=1&f%5B%5D=fixed_version_id&op%5Bfixed_version_id%5D=%3D&v%5Bfixed_version_id%5D%5B%5D=' + version + '&f%5B%5D=tracker_id&op%5Btracker_id%5D=%3D&v%5Btracker_id%5D%5B%5D=6&v%5Btracker_id%5D%5B%5D=12&v%5Btracker_id%5D%5B%5D=13&v%5Btracker_id%5D%5B%5D=14&v%5Btracker_id%5D%5B%5D=15&v%5Btracker_id%5D%5B%5D=17&f%5B%5D=status_id&op%5Bstatus_id%5D=%21&v%5Bstatus_id%5D%5B%5D=6&v%5Bstatus_id%5D%5B%5D=22&f%5B%5D=&c%5B%5D=tracker&c%5B%5D=category&c%5B%5D=status&c%5B%5D=priority&c%5B%5D=subject&c%5B%5D=done_ratio&c%5B%5D=cf_9&c%5B%5D=cf_17&group_by=&limit=100&offset=' + str(
            nextOffset)
        r = requests.get(uri, params={'key': accessKey}, verify=False)
        data = json.loads(r.text)
        total_count = data["total_count"]
        setSize = len(data["issues"])
        for x in xrange(0, setSize):
            issue = RmIssue(data["issues"][x])
            issues.append(issue)
            #done = story.done_ratio
            stories[issue.id] = RmStory(issue)
        nextOffset += setSize

    total_sp = 0
    for issue in issues:
        total_sp += issue.estimated_sp
       
    print "Total story points: %.2f" % (total_sp)
###########################################################


    nextOffset = 0
    total_count = 1
    team_efficiency_index = 0.0
    team_hours_logged = 0.0
    spike_hours = 0.0

    

    
    time_entries = []
    #levi = Dev(4, "Levi", 0, 0)
    bentley = Dev(237, "Bentley", 0, 0 )  #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    isaac = Dev(212, "Isaac", 0, 0)  #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    ryan = Dev(12, "Ryan", 5, 3)  #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    roman = Dev(15, "Roman", 6, 0)  #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    devanand = Dev(331, "Devanand", 0, 0) #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    
    devs = {237: bentley, 212: isaac, 12: ryan, 15: roman, 331: devanand}
    spikes = {}
    for i in issues:
        #print "story %d" % i.id
        devHoursForIssue = {237: 0, 212: 0, 12: 0, 15: 0, 331: 0}
        total_hours_for_issue = 0
        # get time entries
        r = requests.get('https://redmine1h.gdsx.com/redmine/issues/%d/time_entries.json?limit=50' % (i.id),
                         params={'key': accessKey}, verify=False)
        data = json.loads(r.text)

        #print data["total_count"]
        for x in xrange(0, data["total_count"]):

            entry = TimeEntry(data["time_entries"][x])

            team_hours_logged += entry.hours
            
            stories[i.id].spent_hours += entry.hours
            if entry.user_id in devs:
                theDev = devs[entry.user_id]
                if theDev.latestTimeEntryThisSprint is None or entry.updated_on > theDev.latestTimeEntryThisSprint:
                    theDev.latestTimeEntryThisSprint = entry.updated_on
            
            if entry.user_id in devHoursForIssue:
                devHoursForIssue[entry.user_id] += entry.hours
                total_hours_for_issue += entry.hours
        keys = devHoursForIssue.keys()
        if total_hours_for_issue > 0:
            for y in xrange(0, len(keys)):
                devPercByHours = devHoursForIssue[keys[y]] / total_hours_for_issue
                devs[keys[y]].totalSpWorked += i.worked_sp * devPercByHours
                devs[keys[y]].adjustedTotalSpWorked += i.adjusted_worked_sp * devPercByHours
                devs[keys[y]].totalHoursWorked += devHoursForIssue[keys[y]]
    print "total hours logged: %.2f" % (team_hours_logged)
    team_efficiency_index = total_sp / (team_hours_logged)
    
    print "team hourly efficiency (raw): %.2f SP/hr" % (team_efficiency_index)

    
