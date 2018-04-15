from multicorn import ForeignDataWrapper
import sys
from google.oauth2 import service_account
import googleapiclient.discovery
import re
import functools
import time


class googleSheetsFDW(ForeignDataWrapper):

    def __init__(self, options, columns):
        super(googleSheetsFDW, self).__init__(options, columns)
        self.columns = columns
        self.options = options
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        SERVICE_ACCOUNT_FILE = options.get('service_account_file')
        credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        self.service = googleapiclient.discovery.build('sheets', 'v4', credentials=credentials)

    def execute(self, quals, columns):
        """Get range of data from sheet"""
        spreadsheet_id = self.options.get('spreadsheet_id')
        range_name = self.options.get('range_name')
        request = self.service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            majorDimension='ROWS',
            valueRenderOption='UNFORMATTED_VALUE',
            dateTimeRenderOption='SERIAL_NUMBER'
        )

        NCOLUMNS = self.findNofColumns(range_name)
        date_formats = ['date', 'timestamp', 'timestamp without time zone', 'timestamp with time zone', 'time', 'time without time zone', 'time with time zone']

        is_date = [1 if col.type_name in date_formats else 0 for col in self.columns.values()]
        cols_names = [col for col in self.columns]

        data = request.execute()

        if 'values' in data:
            square_data = [[None if j == '' else j for j in i] + [[None] * (NCOLUMNS - len(i))][0] for i in data['values']]
        else:
            square_data = [[None] * NCOLUMNS]

        for idx, ent in enumerate(is_date):
            if ent == 1:
                for idx2, row in enumerate(square_data):
                    square_data[idx2][idx] = self.gsEpochToDate(row[idx])

        response = [dict(zip(cols_names, row)) for row in square_data]
        return response


    def findNofColumns(self, RANGE):
        if '!' not in RANGE: RANGE = '!' + RANGE
        str_start = re.search('!([a-z]*)[0-9]*', str(RANGE).lower()).group(1)
        str_end = re.search(':([a-z]*)[0-9]*', str(RANGE).lower()).group(1)

        arr_start = [(26 ** i) * (ord(x) - 96) for i, x in enumerate(str_start[::-1])]
        arr_end = [(26 ** i) * (ord(x) - 96) for i, x in enumerate(str_end[::-1])]

        col_start = functools.reduce(lambda x, y: x + y, arr_start)
        col_end = functools.reduce(lambda x, y: x + y, arr_end)
        NCOLUMNS = col_end - col_start + 1
        return NCOLUMNS

    def gsEpochToDate(self, epoch):
        try:
            void = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(epoch*24*60*60-2209161600))
        except:
            void = epoch
        return void
