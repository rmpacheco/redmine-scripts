import requests
import json
from redmine import *

nextOffset = 0
total_count=1
issues = []

# read our access key
f = open('key.txt', 'r')
accessKey = f.read()
f.close()

while nextOffset < total_count:
    uri = 'https://redmine1h.gdsx.com/redmine/projects/tla/issues.json?query_id=200&limit=100&offset=' + str(nextOffset)
    
    r = requests.get(uri, params={'key': accessKey}, verify=False)
    data = json.loads(r.text)
    
    total_count = data["total_count"]
    setSize =len(data["issues"])
    for x in xrange (0, setSize):
        issue = RmIssue(data["issues"][x])
        
        # determine if the issue has any children
        issue_rqst = requests.get('https://redmine1h.gdsx.com/redmine/issues/' + str(issue.id) + '.json?include=children', params={'key': accessKey}, verify=False)
        issue_data = json.loads(issue_rqst.text)["issue"]
        # if the issue does not have children and its tracker is not misc, append to our list 
        if ("children" not in issue_data or len(issue_data["children"]) == 0) and issue.tracker_id != 6: #6 = misc
            issues.append(issue)
    nextOffset += setSize

for issue in issues:
    # create a subtask that is a copy of issue with a new tracker, status, and parent
    task = {}
    task["project_id"] = str(issue.json["project"]["id"])
    task["tracker_id"] = 16 # task
    task["status_id"] = 1 # new
    task["priority_id"] = issue.json["priority"]["id"]
    task["subject"] = issue.subject
    task["description"] = issue.description
    task["category_id"] = issue.json["category"]["id"]
    task["fixed_version_id"] = issue.json["fixed_version"]["id"]
    task["parent_issue_id"] = issue.id
    r = requests.post("https://redmine1h.gdsx.com/redmine/issues.json", data=json.dumps({"issue":task}), params={'key': accessKey}, verify=False, headers={'content-type': 'application/json'})
    if r.status_code != requests.codes.created:
        print r
        continue
    else:
        print "Subtask created for %d" % (issue.id) 
    if issue.tracker_id in [12, 13, 14]:  # 12 = feature, 13 = improvement, 14 = bug
        # create a QA task 
        task["priority_id"] = 3 # low
        task["subject"] = 'QA Test "' + issue.subject + "'"
        task["estimated_hours"] = 1
        task["description"] = "Perform QA testing of story \"" + issue.subject + "\".\r\n\r\nThis QA testing should be performed on a test VM and not on a developer box. If time is still available in the sprint, create tasks under the parent story (#" + str(issue.id) + ") to correct any issues discovered"
        r = requests.post("https://redmine1h.gdsx.com/redmine/issues.json", data=json.dumps({"issue":task}), params={'key': accessKey}, verify=False, headers={'content-type': 'application/json'})
        if r.status_code != requests.codes.created:
            print r
        else:
            print "QA task created for %d" % (issue.id)
