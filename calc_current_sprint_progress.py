import requests
import json
from redmine import *
from dateutil import rrule
from datetime import date, datetime, timedelta


def workdays(start, end, holidays=0, days_off=None):
    if days_off is None:
        days_off = 5, 6         # default to: saturdays and sundays
    workdays = [x for x in range(7) if x not in days_off]
    days = rrule.rrule(rrule.DAILY, dtstart=start, until=end,
                       byweekday=workdays)
    return days.count( ) - holidays


nextOffset = 0
total_count=1
total_sp = 0.0
total_worked = 0.0
issues = []

# read our access key
f = open('key.txt', 'r')
accessKey = f.read()
f.close()

while nextOffset < total_count:
    #print "nextOffset = %d, total_count = %d" % (nextOffset, total_count)
    uri = 'https://redmine1h.gdsx.com/redmine/projects/tla/issues.json?query_id=214&limit=100&offset=' + str(nextOffset)
    r = requests.get(uri, params={'key': accessKey}, verify=False)
    data = json.loads(r.text)
    total_count = data["total_count"]
    setSize =len(data["issues"])
    for x in xrange (0, setSize):
        issue = RmIssue(data["issues"][x])
        issues.append(issue)
        if issue.estimated_sp <= 0:
            print (Back.YELLOW + Fore.BLACK + "Warning: Story %d doesn't have a story point estimate" % (self.id) + Back.RESET + Fore.RESET)
        done= issue.done_ratio
        # get story points estimate for the issue
        total_sp += issue.estimated_sp
        total_worked += issue.worked_sp

        #print "story: %d, points: %d, done percentage: %f" % (issue.id, issue.estimated_sp, issue.done_ratio)
    nextOffset += setSize
print "total story points to be worked: %d" % (total_sp)
print "total story points worked so far: %.2f" % (total_worked)
perc_completed_to_date = float(100) * (total_worked / total_sp)
print "percentage of sprint completed so far: %.2f%%" % (perc_completed_to_date)

numBDaysInSprint = 10 #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# determine the sprint start date
# TODO: make this a command line arg (or better yet, make it come from redmine)
sprint_start_date = datetime(2014,12,8)  # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# define number of business hours in this sprint_start_date
bus_hours_per_sprint = 75  # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# determine number of business hours transpired
wd = workdays(sprint_start_date, date.today())
current_time = (datetime.now()-timedelta(hours=8))
current_time_as_float = min(current_time.hour + (current_time.minute/float(60)), 12)
bus_hours_per_day = (bus_hours_per_sprint-3) / (numBDaysInSprint-1)
if wd < numBDaysInSprint:
    bus_hours_by_end_of_wd = wd * (bus_hours_per_day)
else:
    bus_hours_by_end_of_wd= bus_hours_per_sprint

bus_hours_as_of_now = (((wd-1)*bus_hours_per_day) + (current_time_as_float) * .66)
print "business hours as of now = %.2f" % bus_hours_as_of_now
#print "current business hour of the day = %.2f" % (current_time_as_float * .66)
targeted_perc_for_parity = (float(bus_hours_by_end_of_wd) / bus_hours_per_sprint) * 100
if perc_completed_to_date > 0:
    hours_ahead_behind = (bus_hours_as_of_now / (perc_completed_to_date * .01)) - bus_hours_per_sprint
else:
    hours_ahead_behind = bus_hours_per_sprint
#hours_from_completion = (bus_hours_by_end_of_wd / (perc_completed_to_date * .01)) - bus_hours_by_end_of_wd
#print "business hours as of end of today: %d" % (bus_hours_by_end_of_wd)
print "target sprint progress for parity: %.2f%%" % (targeted_perc_for_parity)
if hours_ahead_behind > 0:
    print (Back.RED + Fore.WHITE + "total hours behind : %.2f" % (hours_ahead_behind) + Back.RESET + Fore.RESET)
else:
    print (Back.GREEN + Fore.BLACK+ "total hours ahead : %.2f" % (hours_ahead_behind*-1) + Back.RESET + Fore.RESET)
story_points_behind =  0
if (targeted_perc_for_parity > perc_completed_to_date):
    story_points_behind = (.01) * (targeted_perc_for_parity - perc_completed_to_date) * total_sp
print "story points to complete today for parity: %.2f" % (story_points_behind)

time_entries = []
bentley = Dev(237, "Bentley", 4) #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
isaac = Dev(212, "Isaac") #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
gordon = Dev(128, "Gordon", 0) #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
ryan = Dev(12, "Ryan") #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
roman = Dev(15, "Roman", 1) #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
if wd == numBDaysInSprint:
    ryan.adjustedTotalSpWorked = 2
    gordon.adjustedTotalSpWorked = 1
devs = {237:bentley, 212:isaac, 128:gordon, 12:ryan, 15:roman}
#devNames = {237:"Bentley", 212:"Isaac", 128: "Gordon", 12: "Ryan", 15: "Roman"}
#devSpForSprint = {237:0, 212:0, 128:0, 12:0, 15:0}
for i in issues:
    #print "story %d" % i.id
    devHoursForIssue = {237:0, 212:0, 128:0, 12:0, 15:0}
    total_hours_for_issue = 0
    # get time entries
    r = requests.get('https://redmine1h.gdsx.com/redmine/issues/%d/time_entries.json?limit=50' % (i.id), params={'key': accessKey}, verify=False)
    data = json.loads(r.text)
    for x in xrange (0, data["total_count"]):
        entry = TimeEntry(data["time_entries"][x])
        if entry.spent_on >= sprint_start_date:
            devHoursForIssue[entry.user_id] += entry.hours
            total_hours_for_issue += entry.hours
    keys = devHoursForIssue.keys()
    #print devHoursForIssue
    if total_hours_for_issue > 0:
        for y in xrange(0, len(keys)):
            devPercByHours = devHoursForIssue[keys[y]] / total_hours_for_issue
            devs[keys[y]].totalSpWorked += i.worked_sp * devPercByHours
            devs[keys[y]].adjustedTotalSpWorked += i.adjusted_worked_sp * devPercByHours
            devs[keys[y]].totalHoursWorked+=devHoursForIssue[keys[y]]
    else:
        if i.worked_sp > 0:
            print (Back.YELLOW + Fore.BLACK + "Warning: Story %d claims progress but has 0 spent time recorded" % (i.id) + Back.RESET + Fore.RESET)
total_projected_sp = 0
for dkey in devs.keys():
    dev = devs[dkey]
    dev.busDayEfficiency = (dev.totalSpWorked/(bus_hours_as_of_now-(8*dev.daysOff)))
    dev.adjustedBusDayEfficiency = (dev.adjustedTotalSpWorked/(bus_hours_as_of_now-(8*dev.daysOff)))
    dev.projectedSp = (dev.busDayEfficiency * (bus_hours_per_sprint - bus_hours_as_of_now)) + dev.totalSpWorked
    total_projected_sp += dev.projectedSp

    #dev.totalSpWorked+( dev.hourEfficiency() * (bus_hours_per_sprint-bus_hours_as_of_now))
    #print "%10s:\t%.2f hrs on stories,\t%.2f story points impacted,\tave. sp / hour: %.2f " % (dev.name, dev.totalHoursWorked, dev.totalSpWorked, dev.hourEfficiency())
    print "%10s:\t%.2f hrs on stories,\t%.2f (%.2f) story points impacted,\t%.2f story points projected,\tave. sp / hr logged: %.2f,\tave. sp / bus. hr: %.2f / %.2f (%.2f / %.2f)" % (dev.name, dev.totalHoursWorked, dev.totalSpWorked, dev.adjustedTotalSpWorked, dev.projectedSp, dev.hourEfficiency(), dev.busDayEfficiency, dev.busDayEfficiency * 8,  dev.adjustedBusDayEfficiency, dev.adjustedBusDayEfficiency * 8)

projection_msg = "At the current pace, the team is projected to complete %.2f story points this sprint."
if total_projected_sp >= total_sp:
    print (Back.GREEN + Fore.BLACK + projection_msg % (total_projected_sp) + Back.RESET + Fore.RESET)
else:
    print (Back.RED + Fore.WHITE + projection_msg % (total_projected_sp) + Back.RESET + Fore.RESET)
