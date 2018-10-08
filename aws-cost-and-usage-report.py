#!/usr/bin/env python

import argparse
import datetime
import dateutil.relativedelta as dateutil
import os
import sys

import boto3


OUTPUT_FILE_NAME = "report.csv"
DEFAULT_OUTPUT_FILE = os.path.join(os.path.abspath(os.path.curdir), OUTPUT_FILE_NAME)


def process_arguments(parser):
    args = parser.parse_args()
    days, months = args.days, args.months
    if (type(days) is int) and (type(months) is int):
        parser.print_help()
        print("Error: 'days' and 'months' options are mutually exclusive.")
        sys.exit()
    if days is None and months is None:
        days, months = 0, 1
    output_fpath = args.fpath
    disable_total = args.disable_total
    return days, months, not disable_total, output_fpath


def query_cost_explorer(client, days, months):
    now = datetime.datetime.utcnow()
    end = now.strftime("%Y-%m-%d")
    granularity = "MONTHLY"
    group_by = [{"Type": "DIMENSION", "Key": "LINKED_ACCOUNT"},
                {"Type": "DIMENSION", "Key": "SERVICE"}]
    if months:
        if months == 1:
            start = now.strftime("%Y-%m-01")
        else:
            start = (now - dateutil.relativedelta(months=months-1)).strftime("%Y-%m-01")
    if days:
        start = (now - datetime.timedelta(days=days)).strftime("%Y-%m-%d")
        granularity = "DAILY"
    result = []
    token = None
    time_period = {"Start": start, "End":  end}
    while True:
        kwargs = {}
        if token:
            kwargs = {"NextPageToken": token}
        data = client.get_cost_and_usage(
            TimePeriod=time_period, Granularity=granularity,
            Metrics=["UnblendedCost"], GroupBy=group_by, **kwargs)
        result += data["ResultsByTime"]
        token = data.get("NextPageToken")
        if not token:
            break
    return result


def main():
    ce = boto3.client("ce", "us-east-1")
    parser = argparse.ArgumentParser(description="AWS Simple Cost and Usage Report")
    parser.add_argument("--output", dest="fpath", default=DEFAULT_OUTPUT_FILE,
                        help="output file path (default:%s)" % OUTPUT_FILE_NAME)
    parser.add_argument("--days", type=int, dest="days", default=None,
                        help="get data for daily usage and cost by given days.\
                        (Mutualy exclusive with 'months' option, default: 0)")
    parser.add_argument("--months", type=int, dest="months", default=None,
                        help="get data for monthly usage and cost by given months. \
                        (Mutualy exclusive with 'days' option, default: 1)")
    parser.add_argument("--disable-total", action="store_true", default=False,
                        help="Do not output total cost per day, or month unit.")
    days, months, enable_total, output_fpath = process_arguments(parser)
    data = query_cost_explorer(ce, days, months)
    out_line = ",".join(["Time Period", "Linked Account", "Service",
              "Amount", "Unit", "Estimated"])
    with open(output_fpath, "w") as out_fd:
        out_fd.write(out_line + "\n")
        for result_by_time in data:
            total_cost = 0
            for group in result_by_time["Groups"]:
                account_id = group["Keys"][0]
                service = group["Keys"][1]
                time_start = result_by_time["TimePeriod"]["Start"]
                if months:
                    date_parts = time_start.split("-")
                    time_start = "%s/%s" % (date_parts[1], date_parts[0])
                amount = group["Metrics"]["UnblendedCost"]["Amount"]
                unit = group["Metrics"]["UnblendedCost"]["Unit"]
                estimated = result_by_time["Estimated"]
                out_line = "%s,%s,%s,%s,%s,%s\n" % (time_start,
                    account_id, service, amount, unit, estimated)
                out_fd.write(out_line)
                total_cost += float(amount)
            if enable_total:
                out_fd.write("Total Cost: %s,,,,,\n" % str(total_cost))
    if output_fpath != DEFAULT_OUTPUT_FILE:
        output_fpath = os.path.abspath(output_fpath)
    print("Output written to: %s" % output_fpath)


if __name__ == "__main__":
    main()
