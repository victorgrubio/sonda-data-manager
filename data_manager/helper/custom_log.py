import logging
import colorlog
import os
import time
import shutil
"""Logging methods to handle logs on modules
"""

def check_directory_expired_date(total_time=3600, app_logs_dir="app_logs"):
    """Checks the time a dir is created and updates if it has passed the total time
    
    :param total_time: Time limit to generate new logs, defaults to 3600
    :type total_time: int, optional
    :param app_logs_dir: Folder to store new logs, defaults to "app_logs"
    :type app_logs_dir: str, optional
    """
    try:
        # If not exists
        if not os.path.exists(app_logs_dir):
            print('Create New APP Logs Folder')
            os.makedirs(app_logs_dir)
        else:
            # if exists check the date
            prev_date = os.path.getmtime(app_logs_dir)
            current_date = time.time()

            # Date has expired
            if int(current_date - prev_date) >= total_time:
                print('Update APP Logs folder')
                try:
                    # Delete directory and create it again
                    shutil.rmtree(app_logs_dir)
                    os.makedirs(app_logs_dir)
                except Exception as e:
                    print(e)
    except Exception as e:
        print(e)


def init_logger(dunder_name, log_level="INFO") -> logging.Logger:
    """Creates a logger for the complete program
    
    :param dunder_name: Name of file to generate Logger from
    :type dunder_name: str
    :param log_level: Minimum level to represent logs, defaults to "INFO"
    :type log_level: str, optional
    :return: Logger object
    :rtype: logging.Logger
    """

    log_format = (
        '%(asctime)s - '
        '%(name)s - '
        '%(filename)s:'
        '%(funcName)s '
        '(%(lineno)d) -  '
        '%(levelname)s - '
        '%(message)s'
    )
    bold_seq = '\033[1m'
    colorlog_format = (
        f'{bold_seq} '
        '%(log_color)s '
        f'{log_format}'
    )
    colorlog.basicConfig(format=colorlog_format)
    logger = logging.getLogger(dunder_name)

    if log_level == "DEBUG":
        logger.setLevel(logging.DEBUG)
    elif log_level == "INFO":
        logger.setLevel(logging.INFO)
    elif log_level == "WARNING":
        logger.setLevel(logging.WARNING)
    elif log_level == "ERROR":
        logger.setLevel(logging.ERROR)

    # Logs directory
    parent_dir = os.getenv('videoQA_parentDir')
    app_logs_dir = os.path.join(parent_dir, "app_logs")

    # Output full log
    check_directory_expired_date(app_logs_dir=app_logs_dir)
    log_path = os.path.join(app_logs_dir, "app.log")
    fh = logging.FileHandler(log_path)
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter(log_format)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Output warning log
    log_path_w = os.path.join(app_logs_dir, "app.warning.log")
    fh = logging.FileHandler(log_path_w)
    fh.setLevel(logging.WARNING)
    formatter = logging.Formatter(log_format)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Output error log
    log_path_e = os.path.join(app_logs_dir, "app.error.log")
    fh = logging.FileHandler(log_path_e)
    fh.setLevel(logging.ERROR)
    formatter = logging.Formatter(log_format)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger