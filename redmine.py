from colorama import init
from colorama import Fore, Back, Style
from datetime import datetime

init() #init colorama

class Dev(object):
    def __init__(self, id, name, daysOff=0):
        self.id = id
        self.name = name
        self.totalHoursWorked = 0
        self.totalSpWorked = 0
        self.adjustedTotalSpWorked = 0
        self.daysOff = daysOff
        self.projectedSp = 0
        self.busDayEfficiency = 0
        self.adjustedBusDayEfficiency = 0
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

class RmIssue(object):
    def __init__(self, issue_json):
        self.json = issue_json

        self.id = self.json["id"]

        self.estimated_sp = 0

        # self.spent_hours = 0
        # if "spent_hours" in self.json:
        #     self.spent_hours = self.json["spent_hours"]

        self.estimated_hours = 0
        if "estimated_hours" in self.json:
            self.estimated_hours = self.json["estimated_hours"]
        self.done_ratio = self.json["done_ratio"]
        custom_fields = self.json["custom_fields"]
        self.tracker_id = self.json["tracker"]["id"]
        self.subject = self.json["subject"]
        self.description = self.json["description"]
        if "parent" in self.json:
            self.parent_id = self.json["parent"]["id"]
        else:
            self.parent_id = 0
        self.has_children = None
        if "story_points" in self.json:
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