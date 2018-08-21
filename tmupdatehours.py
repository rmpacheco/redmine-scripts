#!/usr/local/bin/python
import requests
import json
import math
from redmine import *

requests.packages.urllib3.disable_warnings()

morlock_sprint_id = "532" #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
triforce_sprint_id = "531" #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
baseUris = ['https://redmine1h.gdsx.com/redmine/projects/morlock/issues.json?utf8=%E2%9C%93&set_filter=1&f%5B%5D=status_id&op%5Bstatus_id%5D=o&f%5B%5D=tracker_id&op%5Btracker_id%5D=%3D&v%5Btracker_id%5D%5B%5D=16&f%5B%5D=fixed_version_id&op%5Bfixed_version_id%5D=%3D&v%5Bfixed_version_id%5D%5B%5D='+morlock_sprint_id+'&f%5B%5D=&c%5B%5D=tracker&c%5B%5D=status&c%5B%5D=priority&c%5B%5D=subject&c%5B%5D=assigned_to&c%5B%5D=updated_on&c%5B%5D=fixed_version&c%5B%5D=due_date&c%5B%5D=done_ratio&group_by=assigned_to', \
'https://redmine1h.gdsx.com/redmine/projects/tla/issues.json?utf8=%E2%9C%93&set_filter=1&f%5B%5D=status_id&op%5Bstatus_id%5D=o&f%5B%5D=tracker_id&op%5Btracker_id%5D=%3D&v%5Btracker_id%5D%5B%5D=16&f%5B%5D=fixed_version_id&op%5Bfixed_version_id%5D=%3D&v%5Bfixed_version_id%5D%5B%5D='+triforce_sprint_id+'&f%5B%5D=&c%5B%5D=tracker&c%5B%5D=status&c%5B%5D=priority&c%5B%5D=subject&c%5B%5D=done_ratio&c%5B%5D=estimated_hours&group_by=assigned_to']
#baseUris = ['https://redmine1h.gdsx.com/redmine/projects/morlock/issues.json?query_id=369', 'https://redmine1h.gdsx.com/redmine/projects/tla/issues.json?query_id=201' ]
# read our access key
#f = open('key.txt', 'r')
accessKey = "045c0bc5c92989dea17ba6bb51a1f08986c14714" #f.read()
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

