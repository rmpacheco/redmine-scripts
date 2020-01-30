from datetime import datetime
import redmine

# TODO: get start and end dates as input from command line args
beginDate, endDate = datetime(2019, 11, 1), datetime(2020, 1, 1)
versions = redmine.get_sprint_versions(beginDate, endDate)

for v in range(0, len(versions)):
    for issue in redmine.get_issues(versions[v].id):
        versions[v].issues.append(issue)

total_sp = 0
col1, col2, col3, col4 = 5, 15, 10, 10
print ("")
print ("Velocity Metrics: " +  beginDate.strftime("%m/%d/%Y") + " -> " + endDate.strftime("%m/%d/%Y"))
print ("-" * 60)
print (f"%-{col1}s %-{col2}s %-{col3}s %-{col4}s %s" % ("ID", "Name", "TotalSP", "MedianSP", "StdDev"))
print ("-" * 60)
for vv in range(0, len(versions)):        
    total_sp += versions[vv].total_story_points()
    print (f"%-{col1}s %-{col2}s %-{col3}s %-{col4}s %s" % (versions[vv].id, versions[vv].name, 
            ("%.2f" % versions[vv].total_story_points()), ("%.2f" % versions[vv].median_story_points()), 
            ("%.2f" % versions[vv].standard_deviation_points())))

print ("-" * 60)
print (f"%-{col1+col2+1}s %.2f total" % ("", total_sp))
if len(versions) > 0:
    print (f"%-{col1+col2+1}s %.2f average" % ("", total_sp / len(versions)))




    

    
   
    
