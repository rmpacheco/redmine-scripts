#!/usr/local/bin/python
import requests
import json
import math
from redmine import *

requests.packages.urllib3.disable_warnings()

def calcSp(totalHours):
    raw = totalHours * .395
    if raw <= .75:
        return .5
    elif raw <= 1.5:
        return 1
    elif raw <= 2.5:
        return 2
    elif raw <= 4.25:
        return 3
    elif raw <= 6.75:
        return 5
    elif raw <= 11:
        return 8
    elif raw <= 17:
        return 13
    elif raw <= 30:
        return 20

nextOffset = 0
total_count = 1
issues = []

# read our access key
f = open('key.txt', 'r')
accessKey = f.read()
f.close()

while nextOffset < total_count:
    uri = 'https://redmine1h.gdsx.com/redmine/projects/tla/issues.json?query_id=200&limit=100&offset=' + str(nextOffset)
    #uri = 'https://redmine1h.gdsx.com/redmine/projects/tla/issues.json?query_id=201&limit=100&offset=' + str(nextOffset)

    r = requests.get(uri, params={'key': accessKey}, verify=False)
    data = json.loads(r.text)

    total_count = data["total_count"]
    setSize = len(data["issues"])
    for x in xrange(0, setSize):
        print "Story %d" % (data["issues"][x]["id"])

        issue = RmIssue(data["issues"][x])
        if issue.status == 13 and (issue.estimated_sp is None or issue.estimated_sp == 0):
            # pending release without a story point estimate.  back into it from hours
            
        
            total_hours_for_issue = 0
            # get time entries
            entries_response = requests.get(
                'https://redmine1h.gdsx.com/redmine/issues/%d/time_entries.json?limit=50' % issue.id,
                params={'key': accessKey}, verify=False)
            time_entries = json.loads(entries_response.text)
            for j in xrange(0, time_entries["total_count"]):
                entry = TimeEntry(time_entries["time_entries"][j])
                total_hours_for_issue += entry.hours

            
            if total_hours_for_issue > 0 :
                updatedIssue = {"story_points": calcSp(total_hours_for_issue),
                                "notes": "updating story point estimate"}
                entries_update_response = requests.put(
                    "https://redmine1h.gdsx.com/redmine/issues/" + str(issue.id) + ".json",
                    data=json.dumps({"issue": updatedIssue}),
                    params={'key': accessKey}, verify=False, headers={'content-type': 'application/json'})
                if entries_update_response.status_code != requests.codes.ok:
                    print "Got %s for %d" % ( entries_update_response.status_code ,issue.id)
                    continue
                else:
                    print "updated estimated hours for %d" % issue.id
            else:
                print "no need to update %d" % issue.id

    nextOffset += setSize

