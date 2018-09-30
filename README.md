# AWS cost explorer report

Simple reporting tool to extract AWS cost on a daily, or monthly basis in regard
with used services.


## Running the report

### Prerequisites

You must run the tool with **python3** and [AWS SDK for Python ](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) installed. To install the SDK you must run ``` pip3 install boto3 ```.

Your AWS account credentials must be setup in **$HOME/.aws/credentials** file.


It's recommented to use virtualenv though. As guide, take a look into the following
command line example:

```
python3 -v venv venv3
source venv3/bin/activate
pip install boto3

python aws-cost-and-usage-report.py
```

### Usage

By default the script will query the cloud for cost of the current month, which is equivalent with running it with **--month 1** option.

Tool's help options are the following.

```
python aws-cost-and-usage-report.py  -h
usage: aws-cost-and-usage-report.py [-h] [--output FPATH] [--days DAYS]
                                    [--months MONTHS] [--disable-total]

AWS Simple Cost and Usage Report

optional arguments:
  -h, --help       show this help message and exit
  --output FPATH   output file path (default:report.csv)
  --days DAYS      get data for daily usage and cost by given days. (Mutualy
                   exclusive with 'months' option, default: 0)
  --months MONTHS  get data for monthly usage and cost by given months.
                   (Mutualy exclusive with 'days' option, default: 1)
  --disable-total  Do not output total cost per day, or month unit.

```
