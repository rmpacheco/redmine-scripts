import json
import sys

import requests

from redmine import *

sp_per_hour_ratio = .54  # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<

if len(sys.argv) <= 1:
    print "Sprint ID required as command line arg"
else:
    # read our access key
    f = open('key.txt', 'r')
    accessKey = f.read()
    f.close()

    version = sys.argv[1]

    nextOffset = 0
    total_count = 1
    stories = []

    while nextOffset < total_count:
        uri = 'https://redmine1h.gdsx.com/redmine/projects/tla/issues.json?set_filter=1&f%5B%5D=fixed_version_id&op%5Bfixed_version_id%5D=%3D&v%5Bfixed_version_id%5D%5B%5D=' + version + '&f%5B%5D=tracker_id&op%5Btracker_id%5D=%3D&v%5Btracker_id%5D%5B%5D=6&v%5Btracker_id%5D%5B%5D=12&v%5Btracker_id%5D%5B%5D=13&v%5Btracker_id%5D%5B%5D=14&v%5Btracker_id%5D%5B%5D=15&v%5Btracker_id%5D%5B%5D=17&f%5B%5D=status_id&op%5Bstatus_id%5D=%21&v%5Bstatus_id%5D%5B%5D=6&v%5Bstatus_id%5D%5B%5D=22&f%5B%5D=&c%5B%5D=tracker&c%5B%5D=category&c%5B%5D=status&c%5B%5D=priority&c%5B%5D=subject&c%5B%5D=done_ratio&c%5B%5D=cf_9&c%5B%5D=cf_17&group_by=&limit=100&offset=' + str(
            nextOffset)
        r = requests.get(uri, params={'key': accessKey}, verify=False)
        data = json.loads(r.text)
        total_count = data["total_count"]
        setSize = len(data["issues"])
        for x in xrange(0, setSize):
            story = RmIssue(data["issues"][x])
            stories.append(story)
            done = story.done_ratio
        nextOffset += setSize

    print "Story,Tracker,SP Estimate,Expected Hrs,Actual Hrs, Diff (Raw), Diff (%)"
    for story in stories:
        expected = float(story.estimated_sp) / sp_per_hour_ratio
        # get actual hours spent on the story
        actual = 0
        r = requests.get('https://redmine1h.gdsx.com/redmine/issues/%d/time_entries.json?limit=50' % (story.id),
                         params={'key': accessKey}, verify=False)
        data = json.loads(r.text)
        for x in xrange(0, data["total_count"]):
            actual += TimeEntry(data["time_entries"][x]).hours
        diff = expected - actual
        diff_perc = (diff / expected) * 100
        print "%s,%s,%d,%.2f,%.2f,%.2f,%.2f%%" % (
            story.id, story.tracker_id, story.estimated_sp, expected, actual, diff, diff_perc)
    