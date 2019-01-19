import json
import os
import boto3
import uuid
import re
import sys

from datetime import datetime
from merger import merge_pdfs
from add_footer import add_footer


def handle(event, context):
    path = event['Records'][0]['s3']['object']['key']
    bucket = event['Records'][0]['s3']['bucket']['name']

    #* Estos archivos no necesitan se mergeados
    excluded_filenames = [
        'RECIBO',        # pdfs/admin_1/edif_2/expenses/4/RECIBO-DE-PAGO-URENA-RAEL-UF-5-UF-4-5A-4A-ENERO-2019.pdf
        'COBRANZAS',     # pdfs/admin_1/edif_2/expenses/4/URENA-RAEL-HOJA-DE-COBRANZAS-MES-ENERO-2019.pdf
        'account-status'  # pdfs/admin_1/edif_2/expenses/4.account-status.pdf
    ]

    for filename in excluded_filenames:
        if re.search(filename, path):
            sys.exit("No es necesario mergear")

    expense_id = get_expense_id(path)
    account_status_path = get_account_status_path(path, expense_id)

    s3 = boto3.resource('s3')

    s3.Bucket(bucket).download_file(path, "/tmp/expense.pdf")
    s3.Bucket(bucket).download_file(
        account_status_path, "/tmp/account-status.pdf")

    merge_pdfs()
    add_footer()

    client = boto3.client('s3')
    client.upload_file("/tmp/merged_footer.pdf", bucket, path)

    return {
        'statusCode': '200',
        'body': 'Done!',
        'headers': {
            'Content-Type': 'application/json',
        },
    }


def get_expense_id(path):
    expense_id = None

    for i in path.split('/'):
        if (re.match(r'^[\d]$', i)):
            expense_id = i
            break

    return expense_id


def get_account_status_path(path, expense_id):

    path = path.split('/')
    path.pop()
    path = '/'.join(path)
    path = path + '/' + expense_id + '.account-status.pdf'

    return path


if __name__ == "__main__":
    handle(None, None)
