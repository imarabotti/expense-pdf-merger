import re
import time
import json

import boto3
from botocore import exceptions

from add_footer import add_footer
from merger import merge_pdfs


def handle(event, context):
    s3 = boto3.resource('s3')
    
    message = json.loads(event['Records'][0]['body'])
    bucket = message['bucket']
    
    s3.Bucket(bucket).download_file(message['ruta'], "/tmp/expense.json")
    json_data = json.loads(open("/tmp/expense.json").read())

    path = json_data['ruta']
    ruta_prorrateo = path + ".account-status.pdf"

    #* Lo dejo para loguear el merge
    print(ruta_prorrateo)

    s3.Bucket(bucket).download_file(path, "/tmp/expense.pdf")
    s3.Bucket(bucket).download_file(ruta_prorrateo, "/tmp/account-status.pdf")

    merge_pdfs()
    add_footer()

    s3_client = boto3.client('s3')
    s3_client.upload_file("/tmp/merged_footer.pdf", bucket, path)

    s3_client.delete_object(Bucket=bucket, Key=ruta_prorrateo)

    sqs_client = boto3.client('sqs')

    sqs_client.send_message(
        QueueUrl='https://sqs.us-west-2.amazonaws.com/730404845529/qa_finalize_expense_queue',
        MessageBody=event['Records'][0]['body'],
        DelaySeconds=0
    )

    return {
        'statusCode': '200',
        'body': 'Done!',
        'headers': {
            'Content-Type': 'application/json',
        },
    }
