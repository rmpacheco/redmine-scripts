#!/usr/local/bin/python
import requests
import json
import math
from redmine import *

requests.packages.urllib3.disable_warnings()

nextOffset = 0
total_count = 1
issues = []

# read our access key
f = open('key.txt', 'r')
accessKey = f.read()
f.close()

while nextOffset < total_count:
    uri = 'https://redmine1h.gdsx.com/redmine/projects/tla/issues.json?utf8=%E2%9C%93&set_filter=1&f%5B%5D=status_id&op%5Bstatus_id%5D=c&f%5B%5D=tracker_id&op%5Btracker_id%5D=%3D&v%5Btracker_id%5D%5B%5D=9&v%5Btracker_id%5D%5B%5D=16&f%5B%5D=fixed_version_id&op%5Bfixed_version_id%5D=%3D&v%5Bfixed_version_id%5D%5B%5D=272&f%5B%5D=&c%5B%5D=tracker&c%5B%5D=status&c%5B%5D=priority&c%5B%5D=subject&c%5B%5D=done_ratio&c%5B%5D=category&group_by=assigned_to&limit=100&offset=' + str(nextOffset)
    #uri = 'https://redmine1h.gdsx.com/redmine/projects/tla/issues.json?query_id=201&limit=100&offset=' + str(nextOffset)

    r = requests.get(uri, params={'key': accessKey}, verify=False)
    data = json.loads(r.text)

    total_count = data["total_count"]
    setSize = len(data["issues"])
    for x in xrange(0, setSize):
        print "Issue %d" % (data["issues"][x]["id"])

        issue = RmIssue(data["issues"][x])
        if issue.status == 17:
            # done
            
        
            total_hours_for_issue = 0
            # get time entries
            entries_response = requests.get(
                'https://redmine1h.gdsx.com/redmine/issues/%d/time_entries.json?limit=50' % issue.id,
                params={'key': accessKey}, verify=False)
            time_entries = json.loads(entries_response.text)
            for j in xrange(0, time_entries["total_count"]):
                entry = TimeEntry(time_entries["time_entries"][j])
                total_hours_for_issue += entry.hours

            
            if total_hours_for_issue > 0 and issue.estimated_hours != total_hours_for_issue:
                updatedIssue = {"remaining_hours": 0, "estimated_hours": total_hours_for_issue,
                                "notes": "updating estimated hours"}
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

