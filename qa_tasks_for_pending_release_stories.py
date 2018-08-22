
import json
import sys
import os
import requests
from datetime import datetime, timedelta

requests.packages.urllib3.disable_warnings()


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
release_id = int(sys.argv[1])

print("Story ID,Story Status,Related QA Task,QA Task Has Correct Release Set?")

release_stories_uri = redmine_url + "/projects/compleat-root/issues.json?utf8=%E2%9C%93&set_filter=1&f%5B%5D=release_id&op%5Brelease_id%5D" + \
                            "=%3D&v%5Brelease_id%5D%5B%5D=" + str(release_id) + "&f%5B%5D=tracker_id&op%5Btracker_id%5D=%21&v%5Btracker_id" + \
                            "%5D%5B%5D=4&v%5Btracker_id%5D%5B%5D=8&v%5Btracker_id%5D%5B%5D=9&v%5Btracker_id%5D%5B%5D=17&v%5Btracker_id" + \
                            "%5D%5B%5D=16&v%5Btracker_id%5D%5B%5D=19&v%5Btracker_id%5D%5B%5D=20&f%5B%5D=&c%5B%5D=tracker&c%5B%5D=status" + \
                            "&c%5B%5D=priority&c%5B%5D=subject&c%5B%5D=assigned_to&c%5B%5D=updated_on&c%5B%5D=fixed_version&c%5B%5D=" + \
                            "due_date&c%5B%5D=done_ratio&group_by="
#print release_stories_uri

uris = [release_stories_uri]
cache = {}
cache_file_name = "qatfprs_cache.txt"

def get_issue(issue_id):
    issue_data = None
    if issue_id in cache:
        issue_data = cache[issue_id]
    else:
        issue_data = get_json(
            redmine_url + "/issues/" + str(issue_id) + ".json?include=relations")
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
            issue_status = str(issue["status"]["name"])
            issue_data = get_issue(issue_id)
            # grab the relations
            rel_id = None
            if "relations" in issue_data["issue"]:
                relations = issue_data["issue"]["relations"]
                relations_size = len(relations)
                #print str(relations_size) + " found for Issue " + issue_id
                found_at_least_one = False
                for y in range(0, relations_size):
                    relation = relations[y]
                    rel_id = str(relation["issue_id"])
                    #print "Found related issue " + rel_id + " for issue " + issue_id
                    if rel_id == issue_id:
                        #print "should use issue to id"
                        rel_id = str(relation["issue_to_id"])
                    # pull up the relation data
                    rel_data = get_issue(rel_id)["issue"]
                    related_release_id = None
                    if rel_data["tracker"]["id"] == 9:
                        found_at_least_one = True
                        if "release" in rel_data:
                            if "release" in rel_data["release"]:
                                if "id" in rel_data["release"]["release"]:
                                    related_release_id = rel_data["release"]["release"]["id"]
                        release_set_and_matched = False
                        if release_id == related_release_id:
                            release_set_and_matched = True
                        
                        print str(issue_id) + "," + issue_status + "," + str(rel_id) + "," +  str(release_set_and_matched)                   
                if not found_at_least_one:
                    print str(issue_id) + "," + issue_status + ",,False"
            else:
                #print "relations not found for " + issue_id
                print str(issue_id) + "," + issue_status + ",,False"
        next_offset += set_size
