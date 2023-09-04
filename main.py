import argparse
import datetime
import json
import pandas as pd


def get_timestamp_from_date(dates):
    """
    Given a string date
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
    Get the mean delivery time per minute
    :param diff: difference in time between timestamps
    :param mean_del: the mean of the original delivery times
    :param orig_del: the original delivery time
    :param window_size: the moving average window size
    :return: list of the delivery times
    """
    w = 0
    # final list
    result = []
    for i in range(len(mean_del)):
        result += [mean_del[i]] * int(diff[i])
        w += diff[i]
        if w > window_size:
            result[-int(w - window_size):] = [orig_del[i]] * int(w - window_size)
            w = w - window_size
    return result


def format_output(result, dates, output_file="output.json"):
    """
    Formats the final output
    :param result:
    :param dates: list of dates
    :param output_file:
    :return:
    """
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
    Get the range of the minutes from start of the data stream till last minute
    :param dates: list of strings
    :return: list of data ranges
    """
    start_date = pd.to_datetime(dates[0]).round("min")
    end_date = pd.to_datetime(dates[-1]).ceil("min")
    date_range = pd.date_range(start_date, end_date, freq="min").round("min")
    return date_range


if __name__ == "__main__":
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description="A MVA script")

    # Define positional arguments
    parser.add_argument("input_file", help="Input file path")
    parser.add_argument("window_size", help="Window size")

    # Define optional arguments
    parser.add_argument("-v", "--verbose", help="Enable verbose mode", action="store_true")

    # Parse the command-line arguments
    args = parser.parse_args()

    # Access and use the parsed values
    input_file = args.input_file
    window_size = args.window_size

    dates, orig_del = extract_dates_del_from_json(input_file)
    timestamps = get_timestamp_from_date(dates)
    diff = [(a - b) // 60 for a, b in zip(timestamps[1:], timestamps)]
    mean_del = [orig_del[0]] + [(a + b) / 2 for a, b in zip(orig_del[1:], orig_del)]
    result = get_all_mean_del(diff, mean_del, orig_del, window_size=window_size)
    format_output(result, dates, output_file="output.json")
