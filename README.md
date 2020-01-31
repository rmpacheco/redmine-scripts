# README

## Setup

### Python

These scripts are written to run on [Python 3](https://docs.python.org/3/).  You can follow [this guide](https://realpython.com/installing-python/) for download and installation.

### API Key

For these scripts to be able to successfully authenticate you with the Redmine API, you must have a file named `access_key.txt` in your exectuion directory (I just run in the root directory for the scripts), and that file must contain the Redmine API key found in your [Redmine account profile](https://msptmcredminepr.rqa.concur.concurtech.org/redmine/my/account).

### Requests Library

The `redmine.py` module depends on the [Requests library](https://requests.readthedocs.io/en/master/).  To install, you can use `pip` or `pipenv` (follow the [instructions here](https://requests.readthedocs.io/en/master/user/install/#install)).

## Getting Velocity Metrics

### Usage

`python3 velocity_metrics.py` [begin date] [end date]

### Example

`python3 velocity_metrics.py 11/1/2019  1/1/2020`

### Sample Output

```
Velocity Metrics: 11/01/2019 -> 01/01/2020
------------------------------------------------------------
ID    Name            TotalSP    MedianSP   StdDev
------------------------------------------------------------
782   Sprint 137      2.00       2.00       0.00
783   Sprint 138      4.50       2.00       0.71
786   Sprint 139      12.50      1.00       0.90
------------------------------------------------------------
                      19.00 total
                      6.33 average
```
