#!/usr/local/bin/python
import requests
import pytz
import json
from redmine import *
from dateutil import rrule, tz
from datetime import date, datetime, timedelta
import time
import operator

requests.packages.urllib3.disable_warnings()

def workdays(start, end, holidays=0, days_off=None):
    if days_off is None:
        days_off = 5, 6  # default to: saturdays and sundays
    workdays = [x for x in range(7) if x not in days_off]
    days = rrule.rrule(rrule.DAILY, dtstart=start, until=end,
                       byweekday=workdays)
    return days.count() - holidays 


def addDevStatsRow(title, devs, attr):
    row = title + (" " * (14 - len(title))) + "|"
    for dkey in devs.keys():
        dev = devs[dkey]
        row += ("%15s" % ("%.2f" % getattr(dev, attr)))
    return row

def getDayFactor(dev):
    dayFactor = 8
    # if dev == mosley:
    #     dayFactor = 4
    return dayFactor

def hoursToSP(hours):
	return hours*team_efficiency_index

def isSpike(story):
	return story.estimated_sp == 0 and story.status != 1

class RmStory(object):
    def __init__(self, issue):
        self.id = issue.id
        self.subject = issue.subject
        self.estimated_sp = issue.estimated_sp
        self.worked_sp = issue.worked_sp
        self.remaining_sp = issue.estimated_sp - issue.worked_sp
        self.estimated_hours = issue.estimated_hours
        self.spent_hours = 0
        self.status_name = issue.status_name
        self.status = issue.status
    def getRemainingHours(self):
        return self.estimated_hours - self.spent_hours

nextOffset = 0
total_count = 1
total_sp = 0.0
total_worked_sp = 0.0
team_efficiency_index = 0.0
team_hours_logged = 0.0
spike_hours = 0.0
issues = []

#TODO: read our access key from file
#f = open('key.txt', 'r')
accessKey = "yourkey" #f.read()
#f.close()
stories = {}
while nextOffset < total_count:
    # print "nextOffset = %d, total_count = %d" % (nextOffset, total_count)
    uri = 'https://redmine1h.gdsx.com/redmine/projects/tla/issues.json?query_id=200&limit=100&offset=' + str(nextOffset)
    r = requests.get(uri, params={'key': accessKey}, verify=False)
    data = json.loads(r.text)
    total_count = data["total_count"]
    setSize = len(data["issues"])
    for x in xrange(0, setSize):
        issue = RmIssue(data["issues"][x])
        issues.append(issue)
        if issue.estimated_sp <= 0 and issue.status == 1: # status 1 => new
            print (Back.YELLOW + Fore.BLACK + "Warning: Story %d doesn't have a story point estimate" % (
                issue.id) + Back.RESET + Fore.RESET)
        done = issue.done_ratio
        # get story points estimate for the issue
        total_sp += issue.estimated_sp
        total_worked_sp += issue.worked_sp
        #remaining_sp[str(issue.id) + " - " + issue.subject + ": " + str(issue.estimated_hours - (issue.estimated_hours * (.01 * issue.done_ratio)))] = issue.estimated_sp-issue.worked_sp
        stories[issue.id] = RmStory(issue)

        #print "story: %d, points: %d, done percentage: %f" % (issue.id, issue.estimated_sp, issue.done_ratio)
    nextOffset += setSize
print "total story points to be worked: %d" % (total_sp)
print "total story points worked so far: %.2f" % (total_worked_sp)
perc_completed_to_date = float(100) * (total_worked_sp / total_sp)
print "percentage of sprint completed so far: %.2f%%" % (perc_completed_to_date)

numBDaysInSprint = 9  # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# determine the sprint start date
# TODO: make this a command line arg (or better yet, make it come from redmine)
sprint_start_date = datetime(2016, 8, 16).replace(
    tzinfo=tz.gettz('America/Chicago'))  # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# define number of business hours in this sprint_start_date
bus_hours_per_sprint = 74 # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
halfDay = (bus_hours_per_sprint / numBDaysInSprint) / 2
# determine number of business hours transpired
now = datetime.now(pytz.utc)
if now - sprint_start_date > timedelta(days=11):
    now = sprint_start_date + timedelta(days=11)

wd = workdays(sprint_start_date, now)

current_time = (now - timedelta(hours=8))
current_time_as_float = min(current_time.hour + (current_time.minute / float(60)), 12)
bus_hours_per_day = (bus_hours_per_sprint) / (numBDaysInSprint)
if wd < numBDaysInSprint:
    bus_hours_by_end_of_wd = wd * (bus_hours_per_day)
else:
    bus_hours_by_end_of_wd = bus_hours_per_sprint

bus_hours_as_of_now = (((wd - 1) * bus_hours_per_day) + (current_time_as_float) * .33)
print "business hours as of now: %.2f" % bus_hours_as_of_now
print "business hours remaining: %.2f" % (bus_hours_per_sprint - bus_hours_as_of_now)

# print "current business hour of the day = %.2f" % (current_time_as_float * .66)
targeted_perc_for_parity = (float(bus_hours_by_end_of_wd) / bus_hours_per_sprint) * 100
#hours_from_completion = (bus_hours_by_end_of_wd / (perc_completed_to_date * .01)) - bus_hours_by_end_of_wd
#print "business hours as of end of today: %d" % (bus_hours_by_end_of_wd)
print "target sprint progress for parity: %.2f%%" % (targeted_perc_for_parity)
story_points_behind = 0
if (targeted_perc_for_parity > perc_completed_to_date):
    story_points_behind = (.01) * (targeted_perc_for_parity - perc_completed_to_date) * total_sp
print "story points to complete today for parity: %.2f" % (story_points_behind)

time_entries = []
#levi = Dev(4, "Levi", 0, 0)
bentley = Dev(237, "Bentley", 0, 1 )  #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
isaac = Dev(212, "Isaac", 0, 0)  #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
#gordon = Dev(128, "Gordon", 0, 0)  #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
ryan = Dev(12, "Ryan", 0, 8)  #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
roman = Dev(15, "Roman", 0, 0)  #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
devanand = Dev(331, "Devanand", 0, 0) #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
#mosley = Dev(194, "Mosley", 0, 0)  #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
if wd >= numBDaysInSprint:
    ryan.adjustedTotalSpWorked = 0 #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

devs = {237: bentley, 212: isaac, 12: ryan, 15: roman, 331: devanand}
spikes = {}
#devNames = {237:"Bentley", 212:"Isaac", 128: "Gordon", 12: "Ryan", 15: "Roman"}
#devSpForSprint = {237:0, 212:0, 128:0, 12:0, 15:0}
for i in issues:
    #print "story %d" % i.id

    devHoursForIssue = {237: 0, 212: 0, 12: 0, 15: 0, 331: 0}
    total_hours_for_issue = 0
    # get time entries
    r = requests.get('https://redmine1h.gdsx.com/redmine/issues/%d/time_entries.json?limit=50' % (i.id),
                     params={'key': accessKey}, verify=False)
    data = json.loads(r.text)
    for x in xrange(0, data["total_count"]):
        entry = TimeEntry(data["time_entries"][x])
        team_hours_logged += entry.hours
        if isSpike(i):
        	spike_hours += entry.hours
  
        stories[i.id].spent_hours += entry.hours
        if entry.user_id in devs:
            theDev = devs[entry.user_id]
            if theDev.latestTimeEntryThisSprint is None or entry.updated_on > theDev.latestTimeEntryThisSprint:
                theDev.latestTimeEntryThisSprint = entry.updated_on
                #theDev.latestTimeEntryThisSprint = theDev.latestTimeEntryThisSprint.replace(tzinfo = tz.gettz('UTC'))
        if entry.updated_on >= sprint_start_date:
            if entry.user_id in devHoursForIssue:
                devHoursForIssue[entry.user_id] += entry.hours
            total_hours_for_issue += entry.hours
    keys = devHoursForIssue.keys()
    #print devHoursForIssue
    if total_hours_for_issue > 0:
        for y in xrange(0, len(keys)):
            devPercByHours = devHoursForIssue[keys[y]] / total_hours_for_issue
            if isSpike(i):
            	spikes[i] = total_hours_for_issue            
            else:                
                devs[keys[y]].totalSpWorked += i.worked_sp * devPercByHours
                devs[keys[y]].adjustedTotalSpWorked += i.adjusted_worked_sp * devPercByHours
            devs[keys[y]].totalHoursWorked += devHoursForIssue[keys[y]]
    else:
        if i.worked_sp > 0:
            print Back.YELLOW + Fore.BLACK + "Warning: Story %d claims progress but has 0 spent time recorded" % (
                i.id) + Back.RESET + Fore.RESET

team_efficiency_index = total_worked_sp / (team_hours_logged - spike_hours)
print "total hours logged: %.2f" % (team_hours_logged)
print "spike hours logged: %.2f" % (spike_hours)
print "percentage of time spent on spikes: %.2f%%" % (100 * spike_hours / team_hours_logged)
print "team hourly efficiency (raw): %.2f SP/hr" % (team_efficiency_index)


    
total_projected_sp = 0

if perc_completed_to_date > 0:
    task_hours_remaining = 0
    #hours_ahead_behind = (bus_hours_as_of_now / (perc_completed_to_date * .01)) - bus_hours_per_sprint
    for story in stories.items():
        task_hours_remaining += story[1].getRemainingHours()
	#TODO : this is all wrong.  needs to take into account how many hours each dev is available for rest of sprint    
    hours_ahead_behind = (bus_hours_per_sprint - bus_hours_as_of_now ) - task_hours_remaining
else:
    hours_ahead_behind = bus_hours_per_sprint

# if hours_ahead_behind > 0:
#     print (Back.GREEN + Fore.BLACK + "total hours ahead : %.2f" % (hours_ahead_behind) + Back.RESET + Fore.RESET)
# else:
#     print (Back.RED + Fore.WHITE + "total hours behind : %.2f" % (hours_ahead_behind * -1) + Back.RESET + Fore.RESET)


# list the header
#                       Gordon  Ryan    Isaac   Bentley
#                       ------  ----    -----   -------
header = " " * 15
underline = " " * 15
for dkey in devs.keys():
    dev = devs[dkey]
    header += ("%15s" % dev.name)

for dkey in devs.keys():
    dev = devs[dkey]
    dayFactor = 8
    #if dev == mosley:
    #    dayFactor = 4
    #underline += ("%15s") % ('-' * len(dev.name))
    underline += "---------------"
    dev.busDayEfficiency = (dev.totalSpWorked / (bus_hours_as_of_now - (8 * dev.daysOff)))
    
    #TODO: this is wrong...redo in hours maybe?
    hoursRemaining = bus_hours_per_sprint - bus_hours_as_of_now - (dayFactor * dev.remainingDaysOff)
    #print (dev.name + " hrs remaining: %.2f" % hoursRemaining)
    # psp = dev.totalSpWorked + (bhEff * hoursRemaining)
    dev.projectedSp = dev.totalSpWorked + (dev.busDayEfficiency * hoursRemaining)
    #dev.projectedSp = (dev.busDayEfficiency * (bus_hours_per_sprint - bus_hours_as_of_now - (dayFactor*dev.remainingDaysOff))) + dev.totalSpWorked
    total_projected_sp += dev.projectedSp

if perc_completed_to_date >=100 :
    total_projected_sp = total_sp
    
projection_msg = "At the current pace, the team is projected to complete %.2f story points this sprint."
if total_projected_sp >= total_sp:
    print (Back.GREEN + Fore.BLACK + projection_msg % (total_projected_sp) + Back.RESET + Fore.RESET)
else:
    print (Back.RED + Fore.WHITE + projection_msg % (total_projected_sp) + Back.RESET + Fore.RESET)
print ""

#figure out values from spikes

for i in spikes.keys():
    
    devHoursForIssue = {237: 0, 212: 0, 12: 0, 15: 0, 331: 0}
    total_hours_for_issue = 0
    # get time entries
    r = requests.get('https://redmine1h.gdsx.com/redmine/issues/%d/time_entries.json?limit=50' % (i.id),
                     params={'key': accessKey}, verify=False)
    data = json.loads(r.text)
    for x in xrange(0, data["total_count"]):
        entry = TimeEntry(data["time_entries"][x])
        team_hours_logged += entry.hours
        
        if entry.updated_on >= sprint_start_date:
            if entry.user_id in devHoursForIssue:
                devHoursForIssue[entry.user_id] += entry.hours
            total_hours_for_issue += entry.hours
    spike_sp = total_hours_for_issue * team_efficiency_index
    keys = devHoursForIssue.keys()
    #print devHoursForIssue
    if total_hours_for_issue > 0:
        for y in xrange(0, len(keys)):
            devPercByHours = devHoursForIssue[keys[y]] / total_hours_for_issue
            #devs[keys[y]].totalSpWorked += spike_sp * devPercByHours
            devs[keys[y]].adjustedTotalSpWorked += spike_sp * devPercByHours

# now that we've sorted out the spike values, figure out the adjusted business day efficiency
for dkey in devs.keys():
    dev = devs[dkey]
    dev.adjustedBusDayEfficiency = (dev.adjustedTotalSpWorked / (bus_hours_as_of_now - (8 * dev.daysOff)))



hourlyEfficiencyRaw = "hr eff (raw)  |"
for dkey in devs.keys():
    dev = devs[dkey]
    heff = 0
    if dev.totalHoursWorked > 0:
        heff = dev.totalSpWorked / dev.totalHoursWorked
    hourlyEfficiencyRaw += ("%15s" % ("%.2f" % heff))

hourlyEfficiencyAdj = "hr eff (adj)  |"
for dkey in devs.keys():
    dev = devs[dkey]
    heff = 0
    if dev.totalHoursWorked > 0:
        heff = dev.adjustedTotalSpWorked / dev.totalHoursWorked
    hourlyEfficiencyAdj += ("%15s" % ("%.2f" % heff))

bdEfficiencyRaw = "bd eff (raw)  |"
for dkey in devs.keys():
    dev = devs[dkey]
    bdEfficiencyRaw += ("%15s" % ("%.2f" % (dev.busDayEfficiency * getDayFactor(dev))))

bdEfficiencyAdj = "bd eff (adj)  |"
for dkey in devs.keys():
    dev = devs[dkey]
    bdEfficiencyAdj += ("%15s" % ("%.2f" % (dev.adjustedBusDayEfficiency * getDayFactor(dev))))

latestTimeEntries = "last time log |"
centraltz = tz.gettz('America/Chicago')
for dkey in devs.keys():
    dev = devs[dkey]
    if dev.latestTimeEntryThisSprint is not None:
    #latestTimeEntries += ("%15s" % ("%s" % getattr(dev,"latestTimeEntryThisSprint")))
        latestTimeEntries += ("%15s" % ("%s" % dev.latestTimeEntryThisSprint.astimezone(centraltz).strftime("%a,%H:%M")))
    else:
        latestTimeEntries += ("%15s" % "")

print header
print underline
print latestTimeEntries
print addDevStatsRow("hours logged", devs, "totalHoursWorked")
print underline
print addDevStatsRow("impact (raw)", devs, "totalSpWorked")
print addDevStatsRow("impact (adj)", devs, "adjustedTotalSpWorked")
print addDevStatsRow("impact (proj)", devs, "projectedSp")
print underline
print bdEfficiencyRaw
print bdEfficiencyAdj
print underline
print hourlyEfficiencyRaw
print hourlyEfficiencyAdj
print underline 

# Print out information about each story, sorted from furthest behind to least behind
#sorted_remaining = sorted(remaining_sp.items(), key=operator.itemgetter(1), reverse=True)
sorted_remaining = sorted(stories.items(), key=lambda (k, v): v.remaining_sp, reverse=True)
#stories.items().sort( key=lambda (k,v): v.remaining_sp, reverse=True)
print ""
print "Non-Spiked Stories Remaining" 
print "-" * 75
print ("%-10s %-10s %-8s %-8s %s") % ("SP Left", "Hrs Left", "SP/Hr", "RM #", "Title")
print "-" * 75
for stuple in sorted_remaining:
    story = stuple[1] 
    if story.remaining_sp > 0:
    	if story.spent_hours > 0:
            story_eff = story.worked_sp / story.spent_hours
        else:
            story_eff = 0
        #print ("%.2f SP (%.2f hrs/%.2f eff)     %s - %s" % (story.remaining_sp, story.getRemainingHours(), story_eff, story.id, story.subject))
        print ("%-10s %-10s %-8s %-8s %s") % (("%.2f" % story.remaining_sp), ("%.2f" % story.getRemainingHours()), ("%.2f" % story_eff), story.id, story.subject)
# spikes report

print ""
print "Spikes" 
print "-" * 75
print ("%-10s %-10s %-8s %s") % ("SP Value", "Hrs Spent", "RM #", "Title and Status")
print "-" * 75

for stuple in sorted(stories.items(), key=lambda (k, v): v.spent_hours, reverse=False):
	story = stuple[1]
	if isSpike(story):
		#print ("%.2f SP\t(%.2f hrs spent)\t%s - %s (%s)" % (hoursToSP(story.spent_hours), story.spent_hours, story.id, story.subject, story.status_name))
		print ("%-10s %-10s %-8s %s (%s)") % (("%.2f" % hoursToSP(story.spent_hours)), ("%.2f" % story.spent_hours), story.id, story.subject, story.status_name)
		

