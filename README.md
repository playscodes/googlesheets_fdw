# googlesheets_fdw
An FDW for connecting google spreadsheets as tables for your postgresql database through the multicorn using python 

## Be careful
Only reading available (in current version)

## Required:
- PostgreSQL (tested on v 10.3)
- [Python](https://www.python.org/) (tested on v 3.6)
- [Multicorn ](http://multicorn.org/)

## Install:
- Download and install multicorn
- Clone git and install
```
git clone git://github.com/playscodes/googlesheets_fdw.git
cd googlesheets_fdw
python setup.py install or pip install .
```
- [Create google service account](https://support.google.com/a/answer/7378726?hl=en)
- Download service account credentials .json file
- Share your target document with your service account
- Create your server
```
CREATE
SERVER googlesheets_fdw
foreign data wrapper multicorn
options
(
wrapper 'googlesheets_fdw.googleSheetsFDW',
service_account_file '/path_to_your_credentials.json'
);
```
- Create foreign table
```
CREATE FOREIGN TABLE shema.table_name (
    id bigint, name text
) server googlesheets_fdw options (
    spreadsheet_id 'your_spreadsheet_id',
    range_name '''Sheet_name''!A2:B'
);
```
## Planed:
- write clear tutorial
- add indexes
- add update/delete/insert options
