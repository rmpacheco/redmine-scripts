
import json
import sys
import os
import requests
from datetime import datetime, timedelta

requests.packages.urllib3.disable_warnings()


def get_json(uri):
    accessKey = "youraccesskeyhere"

    r = requests.get(uri, params={'key': accessKey}, verify=False)
    return json.loads(r.text)


redmine_url = "https://msptmcredminepr.rqa.concur.concurtech.org/redmine"

compleat_stories_uri = redmine_url + "/projects/compleat-root/issues.json?utf8=%E2%9C%93"
# release_stories_uri = redmine_url + "/projects/compleat-root/issues.json?utf8=%E2%9C%93&set_filter=1&f%5B%5D=release_id&op%5Brelease_id%5D" + \
#                             "=%3D&v%5Brelease_id%5D%5B%5D=" + str(release_id) + "&f%5B%5D=tracker_id&op%5Btracker_id%5D=%21&v%5Btracker_id" + \
#                             "%5D%5B%5D=4&v%5Btracker_id%5D%5B%5D=8&v%5Btracker_id%5D%5B%5D=9&v%5Btracker_id%5D%5B%5D=17&v%5Btracker_id" + \
#                             "%5D%5B%5D=16&v%5Btracker_id%5D%5B%5D=19&v%5Btracker_id%5D%5B%5D=20&f%5B%5D=&c%5B%5D=tracker&c%5B%5D=status" + \
#                             "&c%5B%5D=priority&c%5B%5D=subject&c%5B%5D=assigned_to&c%5B%5D=updated_on&c%5B%5D=fixed_version&c%5B%5D=" + \
#                             "due_date&c%5B%5D=done_ratio&group_by="
#print release_stories_uri

cache = {}
cache_file_name = "compleat_issues_cache.txt"

def get_issue(issue_id):
    issue_data = None
    if issue_id in cache:
        issue_data = cache[issue_id]
    else:
        issue_data = get_json(
            redmine_url + "/issues/" + str(issue_id) + ".json?include=relations,journals")
        cache[issue_id] = issue_data
        ctext = json.dumps(cache)
        with open(cache_file_name, 'w') as cache_file:
            cache_file.write(ctext)
    return issue_data


if os.path.exists(cache_file_name):
    with open(cache_file_name, 'r') as cache_file:
        ctext = cache_file.read().replace('\n', '')
        if len(ctext) > 0:
            cache = json.loads(ctext)


next_offset = 0
total_count = 1

while next_offset < total_count:
    data = get_json(compleat_stories_uri + '&limit=25&per_page=25&offset=' + str(next_offset))

    total_count = data["total_count"]
    set_size = len(data["issues"])
    for x in range(0, set_size):
        issue = data["issues"][x]
        issue_id = str(issue["id"])
        issue_data = get_issue(issue_id)
        
    next_offset += set_size
