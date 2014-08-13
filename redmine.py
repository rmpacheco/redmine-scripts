from colorama import init
from colorama import Fore, Back, Style
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

class RmIssue(object):
    def __init__(self, issue_json):
        self.json = issue_json
        
        self.id = self.json["id"]
        self.done_ratio = self.json["done_ratio"]
        custom_fields = self.json["custom_fields"]
        self.tracker_id = self.json["tracker"]["id"]
        self.estimated_sp = 0
        self.subject = self.json["subject"]
        self.description = self.json["description"]
        self.has_children = None
        for i in xrange(0, len(custom_fields)):
            cf = custom_fields[i]
            if cf["name"] == "Story Points":
                if cf["value"] != '':
                    self.estimated_sp = int(cf["value"])
                    break
                else:
                    print (Back.YELLOW + Fore.BLACK + "Warning: Story %d doesn't have a story point estimate" % (self.id) + Back.RESET + Fore.RESET)
        self.worked_sp = (self.estimated_sp * (self.done_ratio / float(100)))
        self.adjusted_worked_sp = self.worked_sp
        if self.estimated_sp == 8:
            self.adjusted_worked_sp = self.worked_sp * 1.15
        if self.estimated_sp == 13:
            self.adjusted_worked_sp = self.worked_sp * 1.35
        if self.estimated_sp == 20:
            self.adjusted_worked_sp = self.worked_sp * 1.75