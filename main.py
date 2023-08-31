import argparse
import datetime
import json
import pandas as pd


def get_timestamp_from_date(dates):
    """

    :param dates:
    :return:
    """
    timestamps = []
    for d in dates:
        date_format = datetime.datetime.strptime(d, "%Y-%m-%d %H:%M:%S.%f")
        unix_time = datetime.datetime.timestamp(date_format)
        timestamps.append(unix_time)
    return timestamps


def extract_dates_del_from_json(file):
    """
  https://stackoverflow.com/questions/21058935/python-json-loads-shows-valueerror-extra-data
  """
    data = [json.loads(line) for line in open(file, 'r')]
    print(data)
    dates = [d["timestamp"] for d in data]
    delivery = [d["duration"] for d in data]
    return dates, delivery


def get_all_mean_del(diff, mean_del, orig_del, window_size=10):
    """

    :param diff:
    :param mean_del:
    :param orig_del:
    :param window_size:
    :return:
    """
    w = 0
    # final list
    result = []
    for i in range(len(mean_del)):
        result += [mean_del[i]] * int(diff[i])
        w += diff[i]
        if w > window_size:
            result[-int(w - window_size):] = [orig_del[i]] * int(w - 10)
            w = w - window_size
    return result


def format_output(result, dates, output_file="output.json"):
    # not quite sure if this is a hardcoded case in fact
    date_range = get_range_dates(dates)
    output = [{"date": str(date_range[0]), "average_delivery_time": 0}]
    for d, time in zip(result, date_range[1:]):
        output.append({"date": str(time), "average_delivery_time": d})

    with open(output_file, 'w') as json_file:
        for entry in output:
            json_file.write(json.dumps(entry) + '\n')

    return output


def get_range_dates(dates):
    """

    :param dates: list of strings
    :return:
    """
    start_date = pd.to_datetime(dates[0]).round("min")
    end_date = pd.to_datetime(dates[-1]).ceil("min")
    date_range = pd.date_range(start_date, end_date, freq="min").round("min")
    return date_range


if __name__ == "__main__":
    dates, orig_del = extract_dates_del_from_json("input.json")
    timestamps = get_timestamp_from_date(dates)
    diff = [(a - b) // 60 for a, b in zip(timestamps[1:], timestamps)]
    mean_del = [orig_del[0]] + [(a + b) / 2 for a, b in zip(orig_del[1:], orig_del)]
    result = get_all_mean_del(diff, mean_del, orig_del, window_size=10)
    format_output(result, dates, output_file="output.json")
