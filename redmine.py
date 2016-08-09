from colorama import init
from colorama import Fore, Back, Style
from datetime import datetime
from dateutil import tz

init() #init colorama

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

        self.estimated_sp = 0.0

        # self.spent_hours = 0
        # if "spent_hours" in self.json:
        #     self.spent_hours = self.json["spent_hours"]

        self.estimated_hours = 0.0
        if "estimated_hours" in self.json:
            self.estimated_hours = self.json["estimated_hours"]
        self.done_ratio = self.json["done_ratio"]
        #custom_fields = self.json["custom_fields"]
        self.tracker_id = self.json["tracker"]["id"]
        self.subject = self.json["subject"]
        if "description" in self.json:
            self.description = self.json["description"]
        else:
            self.description = ""
        if "parent" in self.json:
            self.parent_id = self.json["parent"]["id"]
        else:
            self.parent_id = 0
        self.has_children = None
        if "story_points" in self.json:
            if self.json["story_points"] is not None and self.json["story_points"] != "":
                self.estimated_sp = float(self.json["story_points"])
        # for i in xrange(0, len(custom_fields)):
        #     cf = custom_fields[i]
        #     if cf["name"] == "Story Points":
        #         if cf["value"] != '':
        #             self.estimated_sp = int(cf["value"])
        #             break

        self.worked_sp = (self.estimated_sp * (self.done_ratio / float(100)))
        self.adjusted_worked_sp = self.worked_sp
        if self.estimated_sp == 8:
            self.adjusted_worked_sp = self.worked_sp * 1.15
        if self.estimated_sp == 13:
            self.adjusted_worked_sp = self.worked_sp * 1.25
        if self.estimated_sp >= 20:
            self.adjusted_worked_sp = self.worked_sp * 1.5

        if "status" in self.json:
            self.status = self.json["status"]["id"]
            self.status_name = self.json["status"]["name"]
