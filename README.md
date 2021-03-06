# hsbc2ofx: Convert HSBCnet CSV files to OFX

HSBCnet is possibly the worst online banking interface I've been forced to use. We use Quickbooks for our business accounting, and HSBCnet's Quickbooks export does not contain any detailed description about any transaction. It only includes something generic like "DEBIT" and the amount. This makes it nearly impossible to classify transactions.

However, HSBC's Excel export contains the transaction descriptions, so I wrote this script to convert that to an OFX file, which can then be imported into Quickbooks Online. This only works well enough for me to import statements, so these OFX files probably aren't "valid", and the script almost certainly has bugs. Please let me know if you find any, or even better: send me a pull request to fix them!

## Usage

1. One time setup: Edit `hsbc2ofx.py` to add a unique BANKID and ACCOUNTID at the top of the file. Example:

    ```
    BANKID=12345
    ACCOUNTID=456789
    ```
2. In HSBCnet: Save account information in Excel format
3. Open the file in Excel and export it to CSV (or see html2csv below)
4. Convert: `./hsbc2ofx.py (input csv file) > (output ofx file)`
5. Upload the OFX file to Quickbooks Online.


## html2csv

If you have Go installed, you can use this program to convert HSBCnet's "Excel export" (which is actually HTML) to CSV:

1. One time compile: go build html2csv.go
2. ./html2csv (input file) > output.csv
