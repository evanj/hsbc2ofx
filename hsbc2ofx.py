#!/usr/bin/python

# Takes a CSV from HSBCnet's Excel output and transforms it into OFX

# SEE SPEC:
# https://fi.intuit.com/ofximplementation/dl/wc_spec.pdf


import csv
import math
import sys
import time

# Substitute your bank ID and account ID here:
BANKID = None
ACCOUNTID = None

if BANKID is None or ACCOUNTID is None:
    raise Exception("Set BANKID and ACCOUNTID in the header of hsbc2ofx.py")

# Previously, TRN type was returned as an integer. Now it seems to be a string
OLD_NUMERIC_TYPE_MAP = {
  524: 'XFER',  # transfer credit
  540: 'INT',  # Interest payment
  900: 'CHECK',  # Check
  945: 'POS',  # POS debit withdrawl?
  962: 'DIRECTDEBIT',  # ACH debit initiated by other (e.g. Oxford health, Amex)
  963: 'XFER',  # transfer debit?
  973: 'SRVCHG',  # service charge e.g. ACH fee
  998: 'PAYMENT',  # ACH payment
}

TRN_TYPE_MAP = {
  'TRANSFER': 'CREDIT',
  'BULK': 'DEBIT',
  'CHECK': 'CHECK',
  'CREDIT': 'CREDIT',
  'TT': 'INT',
  'DEPOSIT': 'DEP',
}


def amount_to_float(amount_string):
  if amount_string == '':
    return None

  # HSBC includes commas as the thousands separator: remove
  amount_string = amount_string.replace(',', '')
  return float(amount_string)


def main():
  input_path = sys.argv[1]
  dialect = csv.Sniffer().sniff(open(input_path).read())
  f = open(input_path)
  lines = f.read().splitlines()
  f.close()
  reader = csv.reader(lines[1:], csv.excel)

  end_date_now = time.strftime('%Y%m%d', time.gmtime())

  print '''\nOFXHEADER:100
DATA:OFXSGML
VERSION:102
SECURITY:NONE
ENCODING:USASCII
CHARSET:1252
COMPRESSION:NONE
OLDFILEUID:NONE
NEWFILEUID:NONE

<OFX>
    <SIGNONMSGSRSV1>
        <SONRS>
            <STATUS>
                <CODE>0</CODE>
                <SEVERITY>INFO</SEVERITY>
            </STATUS>
            <DTSERVER>%s</DTSERVER>
            <LANGUAGE></LANGUAGE>
        </SONRS>
    </SIGNONMSGSRSV1>
    <BANKMSGSRSV1>
        <STMTTRNRS>
            <TRNUID>1</TRNUID>
            <STATUS>
                <CODE>0</CODE>
                <SEVERITY>INFO</SEVERITY>
            </STATUS>
            <STMTRS>
            <CURDEF>USD</CURDEF>
            <BANKACCTFROM>
                <BANKID>%s</BANKID>
                <ACCTID>%s</ACCTID>
                <ACCTTYPE>CHECKING</ACCTTYPE>
            </BANKACCTFROM>

            <BANKTRANLIST>
                <DTSTART>19700101</DTSTART>
                <DTEND>%s</DTEND>\n''' % (end_date_now, BANKID, ACCOUNTID, end_date_now)

  for row in reader:
    # account_name, account_number, bank_name, currency, country, bic, iban, account_status, account_type, bank_reference, narrative, customer_reference, trn_type, credit, debit, balance, date = row
    account_name, account_number, bank_name, currency, country, account_status, account_type, bank_reference, narrative, customer_reference, trn_type, credit, debit, balance, date = row

    credit = amount_to_float(credit)
    debit = amount_to_float(debit)
    balance = amount_to_float(balance)

    assert trn_type in TRN_TYPE_MAP, "unknown TRN Type: " + str(trn_type)

    ofx_type = TRN_TYPE_MAP[trn_type]
    day, month, year = date.split('/')

    amount = debit
    if credit is not None:
      assert debit is None
      amount = credit
    assert amount is not None

    # Fake an ID with date + amount
    fitid = '%s%s%s%.2f' % (year, month, day, math.fabs(amount))

    indent = '                '
    print '%s<STMTTRN>' % (indent)
    print '%s    <TRNTYPE>%s</TRNTYPE>' % (indent, ofx_type)
    print '%s    <DTPOSTED>%s%s%s</DTPOSTED>' % (indent, year, month, day)
    print '%s    <TRNAMT>%.2f</TRNAMT>' % (indent, amount)
    # if ofx_type == 'CHECK':
    #   print '%s    <CHECKNUM>%s</CHECKNUM>' % (indent, customer_reference)
    print '%s    <FITID>%s</FITID>' % (indent, fitid)
    print '%s    <NAME>%s</NAME>' % (indent, narrative)
    print '%s    <MEMO></MEMO>' % (indent)
    print '%s</STMTTRN>' % (indent)


  print '''            </BANKTRANLIST>
                <LEDGERBAL>
                    <BALAMT>17752.42</BALAMT>
                    <DTASOF>20130930</DTASOF>
                </LEDGERBAL>
            </STMTRS>
        </STMTTRNRS>
    </BANKMSGSRSV1>
</OFX>
'''

  # writer = csv.writer(sys.stdout, csv.excel)
  # for row in reader:
  #   writer.writerow(row)


if __name__ == '__main__':
  if len(sys.argv) != 2:
    sys.stderr.write('hsbc2ofx.py (input CSV)\n')
    sys.exit(1)
  sys.exit(main())
