import os
import datetime
import sys
import threading
import queue
from src.constants.constants import Constants

log_file_path = "log.txt"

RED = "\033[91m"
GREEN = "\033[92m"
RESET = "\033[0m"

if not os.path.exists(log_file_path):
    with open(log_file_path, "w") as log_file:
        log_file.write("")

# Write space and date to log file to indicate a new run
now = datetime.datetime.now()
with open(log_file_path, "a") as log_file:
    log_file.write("\n")
    log_file.write("-" * 100)
    log_file.write(f"\n{now.strftime('%Y-%m-%d %H:%M:%S')}\n")
    log_file.write("-" * 100)
    log_file.write("\n\n")


class Logger:
    def __init__(self, web_server):
        self.web_server = web_server
        self.log_queue = queue.Queue()
        self.log_thread = threading.Thread(target=self._process_log_queue, daemon=True)
        self.log_thread.start()

    def log(self, message, force_log=False, force_no_log=False):
        self.log_queue.put((message, force_log, force_no_log))

    def _process_log_queue(self):
        while True:
            message, force_log, force_no_log = self.log_queue.get()
            log(message, self.web_server, force_log, force_no_log)
            self.log_queue.task_done()


def log(message, web_server, force_log=False, force_no_log=False):
    """
    Write message to log file and print to console
    """
    if Constants.print_terminal and not force_no_log:
        print(message)
        sys.stdout.flush()

    if web_server and Constants.print_terminal and not force_no_log:
        web_server.log_message(message)

    if Constants.log or force_log and not force_no_log:
        message = str(message).replace(RED, "").replace(GREEN, "").replace(RESET, "")

        # If file is over 25MB, remove the first 100 lines
        if os.path.getsize(log_file_path) > 25 * 1024 * 1024:
            with open(log_file_path, "r") as file:
                lines = file.readlines()
            with open(log_file_path, "w") as file:
                file.writelines(lines[100:])

        with open(log_file_path, "a") as file:
            file.write(
                f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:{message}\n"
            )
