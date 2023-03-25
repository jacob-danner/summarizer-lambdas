import boto3
from dotenv import load_dotenv
import os
import json
import logging

from utils import wait_for_pdf_upload, convert_and_save, upload, cleanup

logging.getLogger().setLevel(logging.INFO)

def file_transform_handler(event, context):
    logging.debug(f'Event: {event}')
    
    # folderName is unique identifier
    body = event['body']
    FOLDER_NAME = json.loads(body)['folderName']
    logging.info(f'Folder Name: {FOLDER_NAME}')

    load_dotenv()
    ACCESS_KEY_ID=os.environ['ACCESS_KEY_ID']
    SECRET_ACCESS_KEY=os.environ['SECRET_ACCESS_KEY']
    BUCKET_NAME=os.environ['BUCKET_NAME']

    cwd = os.getcwd()

    try: 
        s3 = boto3.client(
            's3',
            aws_access_key_id=ACCESS_KEY_ID,
            aws_secret_access_key=SECRET_ACCESS_KEY
        )

        cloud_pdf_path = wait_for_pdf_upload(BUCKET_NAME, s3, FOLDER_NAME)

        # download file from s3 to local
        local_pdf = '/tmp/uploaded.pdf'
        try:
            s3.download_file(BUCKET_NAME, cloud_pdf_path, local_pdf)
        except Exception as e:
            logging.error(f'An error occured trying to download the PDF from S3: {e}')

        image_paths = convert_and_save(local_pdf)
        cloud_image_paths = upload(BUCKET_NAME, s3, FOLDER_NAME, image_paths)
        cleanup(local_pdf, image_paths) 

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            "body": json.dumps(cloud_image_paths)
        }

    except:
        return {
            "statusCode": 400,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            "body": "error"
        }