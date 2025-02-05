import os
import datetime
import sys
from src.constants.constants import Constants

log_file = "log.txt"

RED = "\033[91m"
GREEN = "\033[92m"
RESET = "\033[0m"

if not os.path.exists(log_file):
    with open(log_file, "w") as file:
        file.write("")

# write space and date to log file to indicate a new run
now = datetime.datetime.now()
with open(log_file, "a") as file:
    file.write("\n")
    file.write("-" * 100)
    file.write(f"\n{now.strftime('%Y-%m-%d %H:%M:%S')}\n")
    file.write("-" * 100)
    file.write("\n\n")


def log(message, force_log=False, force_no_log=False):
    """
    Write message to log file and print to console
    :param message: the message to write to the log file
    :param force_log: whether to force log to file
    :param force_no_log: whether to force not to log to file
    :return:
    """
    if Constants.print_terminal:
        print(message)
        sys.stdout.flush()

    if Constants.log or force_log and not force_no_log:
        message = str(message).replace(RED, "").replace(GREEN, "").replace(RESET, "")

        # if file is over one gigabyte remove the first 100 lines
        if os.path.getsize(log_file) > 25 * 1024 * 1024:
            with open(log_file, "r") as file:
                lines = file.readlines()
            with open(log_file, "w") as file:
                file.writelines(lines[100:])

        with open(log_file, "a") as file:
            file.write(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}]:{message}\n")
