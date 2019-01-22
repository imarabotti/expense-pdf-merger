import json
import os
import boto3
import uuid
import re
import sys
import time

from datetime import datetime
from merger import merge_pdfs
from add_footer import add_footer


def handle(event, context):
    path = event['Records'][0]['s3']['object']['key']
    bucket = event['Records'][0]['s3']['bucket']['name']

    #* Estos archivos no necesitan se mergeados
    excluded_filenames = [
        'RECIBO',
        'COBRANZAS',
        'account-status'
    ]

    stop = False

    for filename in excluded_filenames:
        if re.search(filename, path):
            stop = True

    if not stop:
        expense_id = get_expense_id(path)
        account_status_path = get_account_status_path(path, expense_id)

        s3 = boto3.resource('s3')

        print(path)
        print(account_status_path)

        s3.Bucket(bucket).download_file(path, "/tmp/expense.pdf")

        get_account_status_pdf(account_status_path, bucket, s3)

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
    path.pop()  # saco el nombre
    path.pop()  # saco la carpeta de la expensa
    path = '/'.join(path)
    path = path + '/' + expense_id + '.account-status.pdf'

    return path


counter = 0


def get_account_status_pdf(path, bucket, s3):
    global counter

    if counter < 4:
        try:
            s3.Bucket(bucket).download_file(path, "/tmp/account-status.pdf")
        except Exception as e:
            time.sleep(5)
            counter += 1
            get_account_status_pdf(path, bucket, s3)

            pass

    return
