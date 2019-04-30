import json
import os
import re
import time

import boto3
from botocore import exceptions

from add_footer import add_footer
from merger import merge_pdfs


def handle(event, context):
    time.sleep(60)

    s3 = boto3.resource('s3')
    
    bucket = event['Bucket']
    
    try:
        s3.Bucket(bucket).download_file(event['Key'], "/tmp/expense.json")
    except:
        print("No encontre el archivo " + event['Key'])
        return { 'statusCode' : '500' }

    json_data = json.loads(open("/tmp/expense.json").read())

    path = json_data['ruta']
    ruta_prorrateo = path + ".account-status.pdf"
    ruta_sin_prorrateo = path + '.sin-account-status.pdf'

    #* Lo dejo para loguear el merge
    print(ruta_prorrateo)

    s3.Bucket(bucket).download_file(ruta_sin_prorrateo, "/tmp/expense.pdf")
    s3.Bucket(bucket).download_file(ruta_prorrateo, "/tmp/account-status.pdf")

    merge_pdfs()
    add_footer()

    s3_client = boto3.client('s3')
    s3_client.upload_file("/tmp/merged_footer.pdf", bucket, path)

    if json_data['imprime']:
        s3_client.upload_file("/tmp/merged_footer.pdf", bucket, json_data['ruta_impresion'])

    s3_client.delete_object(Bucket=bucket, Key=ruta_prorrateo)
    s3_client.delete_object(Bucket=bucket, Key=ruta_sin_prorrateo)
    s3_client.delete_object(Bucket=bucket, Key=event['Key'])

    return {
        'statusCode': '200',
        'body': 'Done!',
        'headers': {
            'Content-Type': 'application/json',
        },
    }
