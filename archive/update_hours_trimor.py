#!/usr/local/bin/python
import requests
import json
import math
from redmine import *

requests.packages.urllib3.disable_warnings()


baseUris = ['https://redmine1h.gdsx.com/redmine/projects/morlock/issues.json?query_id=369', 'https://redmine1h.gdsx.com/redmine/projects/tla/issues.json?query_id=201' ]
# read our access key
#f = open('key.txt', 'r')
accessKey = "your key" #f.read()
#f.close()
for uriIndex in xrange(0, len(baseUris)):
    nextOffset = 0
    total_count = 1
    issues = []
    while nextOffset < total_count:
        uri = baseUris[uriIndex] + '&limit=100&offset=' + str(nextOffset)
        
        r = requests.get(uri, params={'key': accessKey}, verify=False)
        data = json.loads(r.text)

        total_count = data["total_count"]
        setSize = len(data["issues"])
        for x in xrange(0, setSize):
            print "Issue %d" % (data["issues"][x]["id"])
            issue = RmIssue(data["issues"][x])
            if issue.estimated_hours > 0:
                total_hours_for_issue = 0
                # get time entries
                entries_response = requests.get(
                    'https://redmine1h.gdsx.com/redmine/issues/%d/time_entries.json?limit=50' % issue.id,
                    params={'key': accessKey}, verify=False)
                time_entries = json.loads(entries_response.text)
                for j in xrange(0, time_entries["total_count"]):
                    entry = TimeEntry(time_entries["time_entries"][j])
                    total_hours_for_issue += entry.hours

                remaining_hours = round(issue.estimated_hours - total_hours_for_issue, 2)
                ratio = abs((remaining_hours / issue.estimated_hours) - 1.0) * 100
                # round down to nearest 10
                ratio = int(math.floor(ratio / 10.0)) * 10
                if issue.done_ratio != ratio:
                    updatedIssue = {"remaining_hours": remaining_hours, "done_ratio": ratio,
                                    "notes": "updating remaining hours"}
                    entries_update_response = requests.put(
                        "https://redmine1h.gdsx.com/redmine/issues/" + str(issue.id) + ".json",
                        data=json.dumps({"issue": updatedIssue}),
                        params={'key': accessKey}, verify=False, headers={'content-type': 'application/json'})
                    if entries_update_response.status_code != requests.codes.ok:
                        print "Got %s for %d" % ( entries_update_response.status_code ,issue.id)
                        continue
                    else:
                        print "updated remaining hours for %d" % issue.id
                else:
                    print "no need to update %d" % issue.id

        nextOffset += setSize

