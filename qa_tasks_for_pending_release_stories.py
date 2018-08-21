
import json
import sys
import os
import requests
from datetime import datetime, timedelta

#requests.packages.urllib.disable_warnings()


def get_json(uri):
    accessKey = "c460bd2ac11ee19e084ab30f9c463e1f151cb80e"

    r = requests.get(uri, params={'key': accessKey}, verify=False)
    return json.loads(r.text)


def parse_date_time(dateText):
    return datetime.strptime(dateText, '%Y-%m-%dT%H:%M:%SZ')


def parse_date(dateText):
    return datetime.strptime(dateText, '%Y-%m-%d')

redmine_url = "https://msptmcredminepr.rqa.concur.concurtech.org/redmine"
argSize = len(sys.argv)
release_id = sys.argv[1]

# print("Sprint ID,Sprint Start,Sprint End,Issue ID,Action,Action DateTime,Action Delta from Sprint Start,Story Points,"
#       "Looks like churn?")
print("Story ID,Related QA Task,QA Task Has Correct Release Set?")


# version_data = get_json(
#     redmine_url + "/versions/" + sprint_id + ".json")

# createdDate = parse_date_time(version_data["version"]["created_on"])
# end_date = parse_date(version_data["version"]["due_date"])
# start_date = end_date - timedelta(days=14)

# do two queries.  one that gets items non-closed items and one that gets
# items that were closed after the sprint start date.

# unclosed stories created before end of sprint
release_stories_uri = redmine_url + "/projects/compleat-root/issues.json?utf8=%E2%9C%93&set_filter=1&f%5B%5D=release_id&op%5B" + \
                    "release_id%5D=%3D&v%5Brelease_id%5D%5B%5D=" + release_id + "&f%5B%5D=&c%5B%5D=tracker&c%5B%5D=status&c%5B" + \
                    "%5D=priority&c%5B%5D=subject&c%5B%5D=assigned_to&c%5B%5D=updated_on&c%5B%5D=fixed_version&c%5B%5D=due_date" + \
                    "&c%5B%5D=done_ratio&group_by="

# ucbeos_uri = redmine_url + "/projects/" + pairs[sprint_id] + \
#                 "/issues.json?utf8=%E2%9C%93&set_filter=1&f%5B%5D=closed_on&op%5Bclosed_on%5D=%21*&f%5B%5D" \
#                 "=created_on&op%5Bcreated_on%5D=%3C%3D&v%5Bcreated_on%5D%5B%5D=" + \
#                 version_data["version"]["due_date"] + \
#                 "&f%5B%5D=&c%5B%5D=tracker&c%5B%5D=status&c%5B%5D=priority&c%5B%5D=subject&c%5B%5D=assigned_to&c%5B%5D" \
#                 "=updated_on&c%5B%5D=fixed_version&c%5B%5D=due_date&c%5B%5D=done_ratio&group_by= "

# cascbs_uri = redmine_url + "/projects/" + pairs[sprint_id] + \
#                 "/issues.json?utf8=%E2%9C%93&set_filter=1&f%5B%5D=closed_on&op%5Bclosed_on%5D=%3E%3D&v%5Bclosed_on%5D%5B%5D=" \
#                 + datetime.strftime(createdDate, "%Y-%m-%d") + \
#                 "&f%5B%5D=created_on&op%5Bcreated_on%5D=%3C%3D&v%5Bcreated_on%5D%5B%5D=" \
#                 + version_data["version"]["due_date"] + \
#                 "&f%5B%5D=tracker_id&op%5Btracker_id%5D=%21&v%5Btracker_id%5D%5B%5D=16&f%5B%5D=&c%5B%5D=tracker&c%5B%5D" \
#                 "=status&c%5B%5D=priority&c%5B%5D=subject&c%5B%5D=assigned_to&c%5B%5D=updated_on&c%5B%5D=fixed_version&c%5B" \
#                 "%5D=due_date&c%5B%5D=done_ratio&group_by= "
# uris = [ucbeos_uri, cascbs_uri]
uris = [release_stories_uri]
cache = {}
cache_file_name = "qatfprs_cache.txt"
if os.path.exists(cache_file_name):
    with open(cache_file_name, 'r') as cache_file:
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
                    redmine_url + "/issues/" + str(issue_id) + ".json?include=relations")
                cache[issue_id] = issue_data
                ctext = json.dumps(cache)
                with open(cache_file_name, 'w') as cache_file:
                    cache_file.write(ctext)
            # grab the relations
            if "relations" in issue_data["issue"]:
                relations = issue_data["issue"]["relations"]
                relations_size = len(relations)

                for x in range(0, relations_size):
                    relation = relations[x]
                    # look for a relation involving this version
                    details_size = len(relation["details"])
                    for y in range(0, details_size):
                        det = relation["details"][y]
                        # print(relations[x]["details"][y])
                        # if "name" in det and det["name"] == "fixed_version_id":
                        #     action_delta = parse_date_time(relation["created_on"]) - start_date
                            # if timedelta(days=min_thresh) < action_delta < timedelta(days=max_thresh):
                            #     churn = True
                            # else:
                            #     churn = False

                            # if "new_value" in det and det["new_value"] == str(sprint_id):
                                # print
                                #     f"\"{sprint_id}\",\"{start_date}\",\"{end_date}\",\"{issue_id}\","
                                #     f"\"{'ADDED'}\",\"{relation['created_on']}\",\"{action_delta}\","
                                #     f"\"{str(issue['story_points'])}\",\"{churn}\"")
                            # if "old_value" in det and det["old_value"] == str(sprint_id):
                            #     print(
                            #         f"\"{sprint_id}\",\"{start_date}\",\"{end_date}\",\"{issue_id}\","
                            #         f"\"{'REMOVED'}\",\"{relation['created_on']}\",\"{action_delta}\","
                            #         f"\"{str(issue['story_points'])}\",\"{churn}\"")
        next_offset += set_size
