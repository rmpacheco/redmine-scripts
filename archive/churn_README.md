# Churn calculation script #

You can find the latest version of the church script here:
`https://github.com/rmpacheco/redmine-scripts/blob/master/churn.py`
Feel free to pull from the repo if you want so that you can use git version tracking. 
To use it, you need to invoke it as
`python churn.py <min_threshold> <max_threshold> <sprint_id>:<project_id>`

- min_thresh
  - Lower bound of days after sprint starts during which stories may be added/removed without churn penalty.  For example, since Morlock’s sprints end on a Friday but they don’t plan their next sprint until Monday, I allow 4 days on this value to let them make changes through the first Monday without penalty.
- max_thresh
  - Upper bound of days after sprint starts after which churn penalty is eliminated.  I usually put this at 14 days (meaning changes to sprint on last day of sprint are not penalized since that’s typically when stories that didn’t make it get taken off the sprint)
- sprint_id
  - Numeric sprint ID from redmine (like 502 or 493)
- project_id
  - Redmine project to which the sprint belongs as defined in the URI path (for example, tla, morlock, or gambit)

You may add multiple pairs of sprint ID and project ID if you want to analyze more than one sprint at a time.
Also, a handy tip is to pipe the output out to a .csv file since this script will output in CSV format.  Here’s an example command line:
 `python churn.py 3.7 14 502:tla 508:tla > triforce_churn.csv`