# hsbc2ofx: Convert HSBCnet CSV files to OFX

HSBCnet is possibly the worst online banking interface I've been forced to use. We use Quickbooks for our business accounting, and HSBCnet's Quickbooks export does not contain any detailed description about any transaction. It only includes something generic like "DEBIT" and the amount. This makes it nearly impossible to classify transactions.

However, it turns out that HSBC's Excel export does contain the transaction descriptions, so I wrote this script to convert that to an OFX file which can then be imported into Quickbooks Online. This only works well enough for me to import statements, so I'm nearly certain these OFX files probably aren't "valid", and the script almost certainly has bugs. Please let me know if you find any, or even better: send me a pull request to fix them!

## Usage

1. In HSBCnet: Save account information in Excel format
2. Open the file in Excel and export it to CSV.
3. Convert: `./hsbc2ofx.py (input csv file) > (output ofx file)`
4. Upload the OFX file to Quickbooks Online.
