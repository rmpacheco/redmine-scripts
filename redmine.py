from datetime import datetime
from dateutil import tz
import json
import os
import requests
import math

from dateutil import tz

requests.packages.urllib3.disable_warnings()
base_url = "https://msptmcredminepr.rqa.concur.concurtech.org/redmine"

class Dev(object):
    def __init__(self, id, name, daysOffSoFar=0, remainingDaysOff=0):
        self.id = id
        self.name = name
        self.totalHoursWorked = 0.0
        self.totalSpWorked = 0.0
        self.adjustedTotalSpWorked = 0.0
        self.daysOff = daysOffSoFar
        self.remainingDaysOff = remainingDaysOff
        self.projectedSp = 0.0
        self.busDayEfficiency = 0.0
        self.adjustedBusDayEfficiency = 0.0
        self.latestTimeEntryThisSprint = None
        self.estimatedHoursRemain = 0.0

    def hourEfficiency(self):
        ratio = 0
        if self.totalHoursWorked > 0:
            ratio = float(self.totalSpWorked) / self.totalHoursWorked
        return ratio
    
class TimeEntry(object):
    def __init__(self, entry_json):
        self.json = entry_json
        self.user_id = self.json["user"]["id"]
        self.user_name = self.json["user"]["name"]
        self.hours = float(self.json["hours"])
        self.spent_on = datetime.strptime(self.json["spent_on"], '%Y-%m-%d')
        self.updated_on = datetime.strptime(self.json["updated_on"], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=tz.gettz('UTC'))

class RmIssue(object):
    def __init__(self, issue_json):
        self.json = issue_json
        self.status = 0
        self.status_name=""
        self.id = self.json["id"]
        self.regression = None
        self.estimated_sp = 0.0
        self.closed_on = None
        self.updated_on = None
        self.created_on = None
        self.spent_hours = 0
        if "spent_hours" in self.json:
            self.spent_hours = self.json["spent_hours"]

        self.assigned_id = 0
        if "assigned_to" in self.json:
            self.assigned_id = self.json["assigned_to"]["id"]

        self.estimated_hours = 0.0
        if "estimated_hours" in self.json:
            self.estimated_hours = self.json["estimated_hours"]
        self.done_ratio = self.json["done_ratio"]
        custom_fields = self.json["custom_fields"]
        self.tracker_id = self.json["tracker"]["id"]
        self.subject = self.json["subject"]
        if "description" in self.json:
            self.description = self.json["description"]
        else:
            self.description = ""
        if "closed_on" in self.json:
            self.closed_on = datetime.strptime(self.json["closed_on"], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=tz.gettz('UTC'))
        if "updated_on" in self.json:
            self.updated_on = datetime.strptime(self.json["updated_on"], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=tz.gettz('UTC'))
        if "created_on" in self.json:
            self.created_on = datetime.strptime(self.json["created_on"], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=tz.gettz('UTC'))
        if "parent" in self.json:
            self.parent_id = self.json["parent"]["id"]
        else:
            self.parent_id = 0
        self.has_children = None
        if "story_points" in self.json:
            if self.json["story_points"] is not None and self.json["story_points"] != "":
                self.estimated_sp = float(self.json["story_points"])
        for i in range(0, len(custom_fields)):
            cf = custom_fields[i]
            if cf["name"] == "Regression?":
                self.regression=cf["value"] == 'Regression'
                
        self.worked_sp = (self.estimated_sp * (self.done_ratio / float(100)))
        self.adjusted_worked_sp = self.worked_sp
        if self.estimated_sp == 5:
            self.adjusted_worked_sp = self.worked_sp * 1.25
        if self.estimated_sp >= 8:
            self.adjusted_worked_sp = self.worked_sp * 1.5

        if "status" in self.json:
            self.status = self.json["status"]["id"]
            self.status_name = self.json["status"]["name"]
      
class RmVersion(object):
    def __init__(self, version_json):
        self.id = version_json["id"]
        self.name = version_json["name"]
        if "due_date" in version_json:
            self.due_date = datetime.strptime(version_json["due_date"], '%Y-%m-%d')
            # print (str(self.id) + "- " + self.name + " - " + str(self.due_date))
        else:
            self.due_date = datetime.min
        self.issues = []

    def total_story_points(self):
         return sum([i.estimated_sp for i in self.issues])

    def median_story_points(self):
        lst = [x.estimated_sp for x in self.issues]
        n = len(lst)
        s = sorted(lst)
        return (sum(s[n//2-1:n//2+1])/2.0, s[n//2])[n % 2] if n else None

    def standard_deviation_points(self):
        mean = self.total_story_points() / len(self.issues)
        diffs = [math.pow((i.estimated_sp-mean),2) for i in self.issues]
        mean2 = sum(diffs) / len(diffs)
        return math.sqrt(mean2)


def get_sprint_versions(beginDate, endDate):
    versions = []
    data = get_json(base_url + "/projects/tla/versions.json")
    size = len(data["versions"])
    for x in range(0, size):
        version = RmVersion(data["versions"][x])
        if  version.due_date >= beginDate and version.due_date <= endDate and "sprint" in str.lower(version.name):
            versions.append(version)
    return versions

def get_json(uri):
    if not os.path.exists("access_key.txt"):
        print("Error: Unable to find 'access_key.txt'")
        exit(1)
    with open("access_key.txt", 'r') as keyfile:
        key = keyfile.read().replace('\n', '')

    r = requests.get(uri, params={'key': key}, verify=False)
    return json.loads(r.text)

def get_issues(redmine_version):
    nextOffset = 0
    total_count = 1
    issues = []
    while nextOffset < total_count:
        uri = base_url + '/projects/tla/issues.json?set_filter=1&f%5B%5D=fixed_version_id&op%5Bfixed_version_id%5D=%3D&v%5Bfixed_version_id%5D%5B%5D=' + str(redmine_version) + '&f%5B%5D=tracker_id&op%5Btracker_id%5D=%3D&v%5Btracker_id%5D%5B%5D=6&v%5Btracker_id%5D%5B%5D=12&v%5Btracker_id%5D%5B%5D=13&v%5Btracker_id%5D%5B%5D=14&v%5Btracker_id%5D%5B%5D=15&v%5Btracker_id%5D%5B%5D=17&f%5B%5D=status_id&op%5Bstatus_id%5D=%21&v%5Bstatus_id%5D%5B%5D=6&v%5Bstatus_id%5D%5B%5D=22&f%5B%5D=&c%5B%5D=tracker&c%5B%5D=category&c%5B%5D=status&c%5B%5D=priority&c%5B%5D=subject&c%5B%5D=done_ratio&c%5B%5D=cf_9&c%5B%5D=cf_17&group_by=&limit=100&offset=' + str(
            nextOffset)
        # print (uri)
        data = get_json(uri)
        total_count = data["total_count"]
        setSize = len(data["issues"])
        for x in range(0, setSize):
            issue = RmIssue(data["issues"][x])
            issues.append(issue)
        nextOffset += setSize
    return issues
