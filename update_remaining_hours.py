#!/usr/local/bin/python
import requests
import json
import math
from redmine import *

nextOffset = 0
total_count = 1
issues = []

# read our access key
f = open('key.txt', 'r')
accessKey = f.read()
f.close()

while nextOffset < total_count:
    uri = 'https://redmine1h.gdsx.com/redmine/projects/tla/issues.json?query_id=201&limit=100&offset=' + str(nextOffset)

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

# for issue in issues:
# # create a subtask that is a copy of issue with a new tracker, status, and parent
# task = {}
# task["project_id"] = str(issue.json["project"]["id"])
# task["tracker_id"] = 16 # task
# task["status_id"] = 1 # new
# task["priority_id"] = issue.json["priority"]["id"]
# task["subject"] = issue.subject
#     task["description"] = issue.description
#     task["category_id"] = issue.json["category"]["id"]
#     task["fixed_version_id"] = issue.json["fixed_version"]["id"]
#     task["parent_issue_id"] = issue.id
#     r = requests.post("https://redmine1h.gdsx.com/redmine/issues.json", data=json.dumps({"issue":task}), params={'key': accessKey}, verify=False, headers={'content-type': 'application/json'})
#     if r.status_code != requests.codes.created:
#         print r
#         continue
#     else:
#         print "Subtask created for %d" % (issue.id)
#     if issue.tracker_id in [12, 13, 14]:  # 12 = feature, 13 = improvement, 14 = bug
#         # create a QA task
#         task["priority_id"] = 3 # low
#         task["subject"] = 'QA Test "' + issue.subject + "'"
#         task["estimated_hours"] = .5
#         task["description"] = "Perform QA testing of story \"" + issue.subject + "\".\r\n\r\nThis QA testing should be performed on a test VM and not on a developer box. If time is still available in the sprint, create tasks under the parent story (#" + str(issue.id) + ") to correct any issues discovered"
#         r = requests.post("https://redmine1h.gdsx.com/redmine/issues.json", data=json.dumps({"issue":task}), params={'key': accessKey}, verify=False, headers={'content-type': 'application/json'})
#         if r.status_code != requests.codes.created:
#             print r
#         else:
#             print "QA task created for %d" % (issue.id)
