import requests
import json
from redmine import *

nextOffset = 0
total_count = 1
issues = []

# read my access key
f = open('key.txt', 'r')
accessKey = f.read()
f.close()

seen_parents = []
while nextOffset < total_count:
    uri = 'https://redmine1h.gdsx.com/redmine/projects/tla/issues.json?utf8=%E2%9C%93&set_filter=1&f%5B%5D=status_id&op%5Bstatus_id%5D=*&f%5B%5D=&c%5B%5D=tracker&c%5B%5D=status&c%5B%5D=priority&c%5B%5D=subject&c%5B%5D=assigned_to&c%5B%5D=updated_on&c%5B%5D=fixed_version&c%5B%5D=due_date&c%5B%5D=done_ratio&group_by=&limit=100&offset=' + str(nextOffset)

    r = requests.get(uri, params={'key': accessKey}, verify=False)
    data = json.loads(r.text)

    total_count = data["total_count"]
    setSize = len(data["issues"])
    for x in xrange(0, setSize):

        issue = RmIssue(data["issues"][x])
        # if issue is not a task and issue has a parent task, display it
        if issue.tracker_id != 16:
            if issue.estimated_sp > 0:
                #transfer to new custom field
                updatedIssue = {"story_points": issue.estimated_sp, "notes": "transition to backlogs plugin"}
                r = requests.put("https://redmine1h.gdsx.com/redmine/issues/" + str(issue.id) + ".json",
                                  data=json.dumps({"issue": updatedIssue}),
                                  params={'key': accessKey}, verify=False, headers={'content-type': 'application/json'})
                if r.status_code != requests.codes.ok:
                    print r
                    continue
                else:
                    print "updated story points for %d" % issue.id
            if issue.parent_id > 0:
                # cut off the parent
                #issue.json["parent"]["id"] = 0
                updatedIssue = {"parent_issue_id": "", "notes": "transition to backlogs plugin"}
                r = requests.put("https://redmine1h.gdsx.com/redmine/issues/" + str(issue.id) + ".json",
                                  data=json.dumps({"issue": updatedIssue}),
                                  params={'key': accessKey}, verify=False, headers={'content-type': 'application/json'})
                if r.status_code != requests.codes.ok:
                    print r
                    continue
                else:
                    print "cut off parent for %d" % issue.id

                # establish new relationship instead
                relation = {"issue_to_id": issue.parent_id, "relation_type": "relates"}

                r = requests.post("https://redmine1h.gdsx.com/redmine/issues/" + str(issue.id) + "/relations.json",
                                  data=json.dumps({"relation": relation}), params={'key': accessKey}, verify=False,
                                  headers={'content-type': 'application/json'})
                if r.status_code != requests.codes.created:
                    print r
                    continue
                else:
                    print "established new relationship for %d" % issue.id

                if issue.parent_id not in seen_parents:
                    seen_parents.append(issue.parent_id)

                    print issue.parent_id

    nextOffset += setSize

# for issue in issues:
# # create a subtask that is a copy of issue with a new tracker, status, and parent
# task = {}
#     task["project_id"] = str(issue.json["project"]["id"])
#     task["tracker_id"] = 16 # task
#     task["status_id"] = 1 # new
#     task["priority_id"] = issue.json["priority"]["id"]
#     task["subject"] = issue.subject
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
