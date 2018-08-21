#!/usr/local/bin/python
import requests
import pytz
import json
from redmine import *
from dateutil import rrule, tz
from datetime import date, datetime, timedelta
import time
import operator
import sys
import argparse

requests.packages.urllib3.disable_warnings()

def valid_date(s):
    try:
        return datetime.strptime(s, "%m-%d-%Y").replace(tzinfo=tz.gettz('UTC'))
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)

parser = argparse.ArgumentParser(description='Get regression stats from Redmine.')
parser.add_argument("team", help='the redmine team name')
parser.add_argument('begin', help='the begin date, format MM-DD-YYYY', type=valid_date)
parser.add_argument('end', help='the end date, format MM-DD-YYYY', type=valid_date)
parser.add_argument('-n', '--new', help='only show new regressions reported between begin and end date', action='store_const', const=True)
args = parser.parse_args()
#print(args.accumulate(args.integers))


nextOffset = 0
total_count = 1
issues = []

#TODO: read our access key from file
#f = open('key.txt', 'r')
accessKey = "c460bd2ac11ee19e084ab30f9c463e1f151cb80e" #f.read()
#f.close()
stories = {}
hoursByDow={}

team = args.team
begin = args.begin
end=args.end
onlyNew=args.new

while nextOffset < total_count:
    uri = 'https://msptmcredminepr.rqa.concur.concurtech.org/redmine/projects/'+team+'/issues.json?utf8=%E2%9C%93&set_filter=1&f%5B%5D=cf_29&op%5Bcf_29%5D=*&f%5B%5D=status_id&op%5Bstatus_id%5D=%21&v%5Bstatus_id%5D%5B%5D=6&f%5B%5D=&c%5B%5D=tracker&c%5B%5D=status&c%5B%5D=priority&c%5B%5D=subject&c%5B%5D=assigned_to&c%5B%5D=updated_on&c%5B%5D=fixed_version&c%5B%5D=due_date&c%5B%5D=done_ratio&c%5B%5D=cf_29&group_by=&offset=' + str(nextOffset)
    r = requests.get(uri, params={'key': accessKey}, verify=False)
    data = json.loads(r.text)
    total_count = data["total_count"]
    setSize = len(data["issues"])
    for x in xrange(0, setSize):
        issue = RmIssue(data["issues"][x])
        if onlyNew: #only add issues created during the time window
            if begin <= issue.created_on <= end:
                issues.append(issue)
        else:
            # only add 
            # unclosed issues created before end
            # issues closed after begin
            if (issue.closed_on is None and issue.created_on <= end) or \
               (issue.closed_on is not None and begin <= issue.closed_on):
                issues.append(issue)
     
    nextOffset += setSize

regression_count = sum(1 for i in issues if i.regression == True)
regression_perc = 100*(float(regression_count) / len(issues))

if onlyNew: 
    print "%i new eligible stories, %i regressions (%.2f%%)" % (len(issues), regression_count, regression_perc)
else:
    print "%i eligible stories, %i regressions (%.2f%%)" % (len(issues), regression_count, regression_perc)

for i in issues:
    if i.regression:
        # show the creation date of each regression and, if it closed during window, the closed date as well
        if i.closed_on is not None and begin<=i.closed_on<=end:
            print "%s - Created %s, Closed %s" % (i.id, str(i.created_on), str(i.closed_on))
        else:
            print "%s - Created %s" % (i.id, str(i.created_on))


        # if i.closed_on is not None and i.closed_on <= end:
        #     print "%s - Created %s, Closed %s" % (i.id, str(i.created_on), str(i.closed_on))
        # elif i.closed_on is not None and begin <= i.closed_on <=end:
        #     print "%s - Closed %s" % (i.id, str(i.closed_on))
        # elif i.created_on is not None: # and end >= i.closed_on >= begin:
        #     print "%s - Created %s" % (i.id, str(i.created_on))
        # else:
        #     print "%s"
    
