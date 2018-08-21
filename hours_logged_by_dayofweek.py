
#!/usr/local/bin/python
import requests
import pytz
import json
from redmine import *
from dateutil import rrule, tz
from datetime import date, datetime, timedelta
import time
import operator
import sys

requests.packages.urllib3.disable_warnings()

def translateDow(dow):
	switcher = {
		0: "Monday",
		1: "Tuesday",
        2: "Wednesday",
        3: "Thursday",
        4: "Friday",
        5: "Saturday",
        6: "Sunday",
	}
	return switcher.get(dow, "nothing")


nextOffset = 0
total_count = 1
total_sp = 0.0
total_worked_sp = 0.0
team_efficiency_index = 0.0
team_hours_logged = 0.0
spike_hours = 0.0
issues = []

#TODO: read our access key from file
#f = open('key.txt', 'r')
accessKey = "045c0bc5c92989dea17ba6bb51a1f08986c14714" #f.read()
#f.close()
stories = {}
hoursByDow={}

argSize = len(sys.argv)
team = sys.argv[1]
numDays = str(sys.argv[2])

#team = "morlock"
#numDays = "90"


while nextOffset < total_count:
    # print "nextOffset = %d, total_count = %d" % (nextOffset, total_count)
    uri = 'https://redmine1h.gdsx.com/redmine/projects/'+team+'/issues.json?utf8=%E2%9C%93&set_filter=1&f%5B%5D=tracker_id&op%5Btracker_id%5D=%3D&v%5Btracker_id%5D%5B%5D=4&v%5Btracker_id%5D%5B%5D=8&v%5Btracker_id%5D%5B%5D=9&v%5Btracker_id%5D%5B%5D=6&v%5Btracker_id%5D%5B%5D=12&v%5Btracker_id%5D%5B%5D=13&v%5Btracker_id%5D%5B%5D=14&v%5Btracker_id%5D%5B%5D=15&v%5Btracker_id%5D%5B%5D=17&v%5Btracker_id%5D%5B%5D=19&f%5B%5D=closed_on&op%5Bclosed_on%5D=%3Et-&v%5Bclosed_on%5D%5B%5D='+numDays+'&f%5B%5D=&c%5B%5D=tracker&c%5B%5D=status&c%5B%5D=priority&c%5B%5D=subject&c%5B%5D=assigned_to&c%5B%5D=updated_on&c%5B%5D=fixed_version&c%5B%5D=due_date&c%5B%5D=done_ratio&group_by=' + str(nextOffset)
    #uri ='https://redmine1h.gdsx.com/redmine/projects/morlock/issues.json?utf8=%E2%9C%93&set_filter=1&f%5B%5D=tracker_id&op%5Btracker_id%5D=%3D&v%5Btracker_id%5D%5B%5D=4&v%5Btracker_id%5D%5B%5D=8&v%5Btracker_id%5D%5B%5D=9&v%5Btracker_id%5D%5B%5D=6&v%5Btracker_id%5D%5B%5D=12&v%5Btracker_id%5D%5B%5D=13&v%5Btracker_id%5D%5B%5D=14&v%5Btracker_id%5D%5B%5D=15&v%5Btracker_id%5D%5B%5D=17&v%5Btracker_id%5D%5B%5D=19&f%5B%5D=closed_on&op%5Bclosed_on%5D=%3Et-&v%5Bclosed_on%5D%5B%5D=10&f%5B%5D=&c%5B%5D=tracker&c%5B%5D=status&c%5B%5D=priority&c%5B%5D=subject&c%5B%5D=assigned_to&c%5B%5D=updated_on&c%5B%5D=fixed_version&c%5B%5D=due_date&c%5B%5D=done_ratio&group_by=' + str(nextOffset)
    
   
    r = requests.get(uri, params={'key': accessKey}, verify=False)
    data = json.loads(r.text)
    total_count = data["total_count"]
    setSize = len(data["issues"])
    for x in xrange(0, setSize):
        issue = RmIssue(data["issues"][x])
        issues.append(issue)
     
    nextOffset += setSize

#for each issue in (all issues for triforce in the past 6 months)
for i in issues:
    # get time entries
    r = requests.get('https://redmine1h.gdsx.com/redmine/issues/%d/time_entries.json?limit=50' % (i.id),
                     params={'key': accessKey}, verify=False)
    data = json.loads(r.text)
    for x in xrange(0, data["total_count"]):
        entry = TimeEntry(data["time_entries"][x])
        # group time entries for issue by day of week
        dow = translateDow(entry.spent_on.weekday())
        if dow not in hoursByDow:
        	hoursByDow[dow] = entry.hours
        else:
       		hoursByDow[dow]+=entry.hours
        
sortedHoursByDow = sorted(hoursByDow.items(), key=operator.itemgetter(1))
# print out time entry totals by day of week
print sortedHoursByDow