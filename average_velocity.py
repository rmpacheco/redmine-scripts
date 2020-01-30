import json
import sys
import os
import requests
import string
import math

from datetime import datetime
from dateutil import tz
from redmine import RmIssue

requests.packages.urllib3.disable_warnings()
base_url = "https://msptmcredminepr.rqa.concur.concurtech.org/redmine"
      
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
    stories = {}
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

# TODO: get start and end dates as input from command line args
beginDate = datetime(2019, 11, 1)
endDate = datetime(2020, 1, 1)
versions = get_sprint_versions(beginDate, endDate)

for v in range(0, len(versions)):
    #version_sp = 0
    for issue in get_issues(versions[v].id):
        #version_sp += issue.estimated_sp
        #versions[v].story_points = version_sp
        versions[v].issues.append(issue)

total_sp = 0
col1=5
col2=15
col3=10
col4=10
print ("")
print ("Velocity Metrics: " +  beginDate.strftime("%m/%d/%Y") + " -> " + endDate.strftime("%m/%d/%Y"))
print ("-" * 60)
print (f"%-{col1}s %-{col2}s %-{col3}s %-{col4}s %s" % ("ID", "Name", "TotalSP", "MedianSP", "StdDev"))
print ("-" * 60)
for vv in range(0, len(versions)):        
    total_sp += versions[vv].total_story_points()
    print (f"%-{col1}s %-{col2}s %-{col3}s %-{col4}s %s" % (versions[vv].id, versions[vv].name, ("%.2f" % versions[vv].total_story_points()), ("%.2f" % versions[vv].median_story_points()), ("%.2f" % versions[vv].standard_deviation_points())))

print ("-" * 60)
print (f"%-{col1+col2+1}s %.2f total" % ("", total_sp))
if len(versions) > 0:
    print (f"%-{col1+col2+1}s %.2f average" % ("", total_sp / len(versions)))




    

    
   
    
