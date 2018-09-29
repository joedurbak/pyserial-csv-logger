import serial
from datetime import datetime as dt, timedelta as td
import settings
import os
import re


def create_file_path(directory, prefix, datetime, suffix):
    regex_dt = re.sub(r':', '_', str(datetime))
    filename = "{0}__{1}.{2}".format(prefix, regex_dt, suffix)
    return os.path.join(directory, filename)


def file_exists(file_path):
    try:
        open(file_path, 'r').close()
        return True
    except FileNotFoundError:
        return False


class SerialCSVLogger:
    def __init__(
            self, output_file_prefix=settings.OUTPUT_FILE_PREFIX, output_dir=settings.OUTPUT_FILE_DIR,
            com_port=settings.COM_PORT, baud=settings.BAUD, csv_headers=settings.CSV_HEADERS
    ):
        self.com_port = com_port
        self.output_file_prefix = output_file_prefix
        self.output_dir = output_dir
        self.baud = baud
        self.starting_dt = dt.now()
        self.output_filename = "{0}__{1}.csv".format(self.output_file_prefix, self.starting_dt)
        self.output_file_path = create_file_path(self.output_dir, self.output_file_prefix, self.starting_dt, 'csv')
        self.csv_col_num = len(csv_headers)
        if len(csv_headers) != 0:
            csv_headers.append('datetime')
            self.csv_headers = ','.join(csv_headers) + '\n'
        else:
            self.csv_headers = ''

    def csv_init(self):
        with open(self.output_file_path, 'w') as file:
            file.write(self.csv_headers)
            file.close()

    def csv_log(self, csv_string):
        now = dt.now()
        if len(csv_string.split(',')) == self.csv_col_num:
            if td(days=1) > (now - self.starting_dt):
                if file_exists(self.output_file_path):
                    with open(self.output_file_path, 'a') as file:
                        file.write("{0},{1}\n".format(csv_string.rstrip(), now))
                        file.close()
                else:
                    self.csv_init()
                    self.csv_log(csv_string)
            else:
                self.starting_dt = now
                self.output_file_path = create_file_path(
                    self.output_dir, self.output_file_prefix, self.starting_dt, 'csv'
                )
                self.csv_init()
                self.csv_log(csv_string)

    def monitor(self):
        ser = serial.Serial(port=self.com_port, baudrate=self.baud)
        while True:
            line = ser.readline()
            self.csv_log(line.decode())
