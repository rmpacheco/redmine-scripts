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

versions = {189, 195, 199, 205, 208, 215}



# aggregate all sprint data by dev

for versionId in versions:
    bugCount = 0
    featureCount = 0
    archCount = 0
    bugPoints = 0
    featurePoints = 0
    archPoints = 0
    nextOffset = 0
    total_count=1
    total_sp = 0.0
    total_worked = 0.0
    issues = []
    while nextOffset < total_count:
        uri = 'https://redmine1h.gdsx.com/redmine/projects/tla/issues.json?set_filter=1&f%5B%5D=fixed_version_id&op%5Bfixed_version_id%5D=%3D&v%5Bfixed_version_id%5D%5B%5D=' + str(versionId) + '&f%5B%5D=tracker_id&op%5Btracker_id%5D=%3D&v%5Btracker_id%5D%5B%5D=6&v%5Btracker_id%5D%5B%5D=12&v%5Btracker_id%5D%5B%5D=13&v%5Btracker_id%5D%5B%5D=14&v%5Btracker_id%5D%5B%5D=15&v%5Btracker_id%5D%5B%5D=17&f%5B%5D=status_id&op%5Bstatus_id%5D=%21&v%5Bstatus_id%5D%5B%5D=6&v%5Bstatus_id%5D%5B%5D=22&f%5B%5D=&c%5B%5D=tracker&c%5B%5D=category&c%5B%5D=status&c%5B%5D=priority&c%5B%5D=subject&c%5B%5D=done_ratio&c%5B%5D=cf_9&c%5B%5D=cf_17&group_by=&limit=100&offset=' + str(nextOffset)
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
            if issue.tracker_id == 14 or issue.tracker_id == 13:
                bugCount+=1
                bugPoints+=issue.worked_sp
            elif issue.tracker_id == 12:
                featureCount+=1
                featurePoints+= issue.worked_sp
            else:
                archCount+=1
                archPoints+=issue.worked_sp
        nextOffset += setSize
    print "sprintid: %i, bugs: %i, features: %i, architecture: %i,  bugs points: %i, features points: %i, architecture points: %i\n" %(versionId, bugCount, featureCount, archCount, bugPoints, featurePoints, archPoints)

    

