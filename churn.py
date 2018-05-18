#!/usr/local/bin/python
import json
import sys
import os
import requests
from datetime import datetime, timedelta

requests.packages.urllib3.disable_warnings()


def get_json(uri):
    accessKey = "yourkey"

    r = requests.get(uri, params={'key': accessKey}, verify=False)
    return json.loads(r.text)


def parse_date_time(dateText):
    return datetime.strptime(dateText, '%Y-%m-%dT%H:%M:%SZ')


def parse_date(dateText):
    return datetime.strptime(dateText, '%Y-%m-%d')


pairs = {}
argSize = len(sys.argv)
min_thresh = float(sys.argv[1])
max_thresh = float(sys.argv[2])

for argI in range(3, argSize):
    parts = sys.argv[argI].split(':')
    pairs[parts[0]] = parts[1]

print("Sprint ID,Sprint Start,Sprint End,Issue ID,Action,Action DateTime,Action Delta from Sprint Start,Story Points,"
      "Looks like churn?")
for index, sprint_id in enumerate(pairs):
    version_data = get_json(
        "https://redmine1h.gdsx.com/redmine/versions/" + sprint_id + ".json")

    createdDate = parse_date_time(version_data["version"]["created_on"])
    end_date = parse_date(version_data["version"]["due_date"])
    start_date = end_date - timedelta(days=14)

    # do two queries.  one that gets items non-closed items and one that gets
    # items that were closed after the sprint start date.

    # unclosed stories created before end of sprint
    ucbeos_uri = "https://redmine1h.gdsx.com/redmine/projects/" + pairs[sprint_id] + \
                 "/issues.json?utf8=%E2%9C%93&set_filter=1&f%5B%5D=closed_on&op%5Bclosed_on%5D=%21*&f%5B%5D" \
                 "=created_on&op%5Bcreated_on%5D=%3C%3D&v%5Bcreated_on%5D%5B%5D=" + \
                 version_data["version"]["due_date"] + \
                 "&f%5B%5D=&c%5B%5D=tracker&c%5B%5D=status&c%5B%5D=priority&c%5B%5D=subject&c%5B%5D=assigned_to&c%5B%5D" \
                 "=updated_on&c%5B%5D=fixed_version&c%5B%5D=due_date&c%5B%5D=done_ratio&group_by= "

    cascbs_uri = "https://redmine1h.gdsx.com/redmine/projects/" + pairs[sprint_id] + \
                 "/issues.json?utf8=%E2%9C%93&set_filter=1&f%5B%5D=closed_on&op%5Bclosed_on%5D=%3E%3D&v%5Bclosed_on%5D%5B%5D=" \
                 + datetime.strftime(createdDate, "%Y-%m-%d") + \
                 "&f%5B%5D=created_on&op%5Bcreated_on%5D=%3C%3D&v%5Bcreated_on%5D%5B%5D=" \
                 + version_data["version"]["due_date"] + \
                 "&f%5B%5D=tracker_id&op%5Btracker_id%5D=%21&v%5Btracker_id%5D%5B%5D=16&f%5B%5D=&c%5B%5D=tracker&c%5B%5D" \
                 "=status&c%5B%5D=priority&c%5B%5D=subject&c%5B%5D=assigned_to&c%5B%5D=updated_on&c%5B%5D=fixed_version&c%5B" \
                 "%5D=due_date&c%5B%5D=done_ratio&group_by= "
    uris = [ucbeos_uri, cascbs_uri]

    cache = {}
    if os.path.exists('churn_cache.txt'):
        with open('churn_cache.txt', 'r') as cache_file:
            ctext = cache_file.read().replace('\n', '')
            if len(ctext) > 0:
                cache = json.loads(ctext)

    for uri_index in range(0, len(uris)):
        next_offset = 0
        total_count = 1

        while next_offset < total_count:
            data = get_json(
                uris[uri_index] + '&limit=250&per_page=250&offset=' + str(next_offset))

            total_count = data["total_count"]
            set_size = len(data["issues"])
            for x in range(0, set_size):
                issue = data["issues"][x]
                issue_id = str(issue["id"])
                if issue_id in cache:
                    issue_data = cache[issue_id]
                else:
                    issue_data = get_json(
                        "https://redmine1h.gdsx.com/redmine/issues/" + str(issue_id) + ".json?include=journals")
                    cache[issue_id] = issue_data
                    ctext = json.dumps(cache)
                    with open('churn_cache.txt', 'w') as cache_file:
                        cache_file.write(ctext)
                # grab the journals
                if "journals" in issue_data["issue"]:
                    journals = issue_data["issue"]["journals"]
                    journals_size = len(journals)

                    for x in range(0, journals_size):
                        journal = journals[x]
                        # look for a journal involving this version
                        details_size = len(journal["details"])
                        for y in range(0, details_size):
                            det = journal["details"][y]
                            # print(journals[x]["details"][y])
                            if "name" in det and det["name"] == "fixed_version_id":
                                action_delta = parse_date_time(journal["created_on"]) - start_date
                                if timedelta(days=min_thresh) < action_delta < timedelta(days=max_thresh):
                                    churn = True
                                else:
                                    churn = False

                                if "new_value" in det and det["new_value"] == str(sprint_id):
                                    print(
                                        f"\"{sprint_id}\",\"{start_date}\",\"{end_date}\",\"{issue_id}\","
                                        f"\"{'ADDED'}\",\"{journal['created_on']}\",\"{action_delta}\","
                                        f"\"{str(issue['story_points'])}\",\"{churn}\"")
                                if "old_value" in det and det["old_value"] == str(sprint_id):
                                    print(
                                        f"\"{sprint_id}\",\"{start_date}\",\"{end_date}\",\"{issue_id}\","
                                        f"\"{'REMOVED'}\",\"{journal['created_on']}\",\"{action_delta}\","
                                        f"\"{str(issue['story_points'])}\",\"{churn}\"")
            next_offset += set_size
