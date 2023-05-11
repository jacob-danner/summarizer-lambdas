import asyncio
import aioboto3
from dotenv import load_dotenv
import os
import json
import logging

from utils import wait_for_pdf_upload, convert_and_save, upload, cleanup

logging.getLogger().setLevel(logging.INFO)

async def file_transform_handler(event, context):
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
    session = aioboto3.Session()

    try: 
        async with session.client(
            's3',
            aws_access_key_id=ACCESS_KEY_ID,
            aws_secret_access_key=SECRET_ACCESS_KEY
        ) as s3_client: 

            # download pdf
            cloud_pdf_path = await wait_for_pdf_upload(BUCKET_NAME, s3_client, FOLDER_NAME)
            local_pdf = '/tmp/uploaded.pdf'
            try:
                await s3_client.download_file(BUCKET_NAME, cloud_pdf_path, local_pdf)
            except Exception as e:
                logging.error(f'An error occured trying to download the PDF from S3: {e}')

            image_paths = convert_and_save(local_pdf)
            cloud_image_paths = await upload(BUCKET_NAME, s3_client, FOLDER_NAME, image_paths)
            cleanup(local_pdf, image_paths) 

            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST',
                    'Content-Type': 'application/json'
                },
                "isBase64Encoded": False,
                "content-type": "application/json",
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

def lambda_handler(event, context):
    loop = asyncio.get_event_loop()    
    return loop.run_until_complete(file_transform_handler(event, context))