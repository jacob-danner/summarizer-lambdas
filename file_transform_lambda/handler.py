import boto3
from utils import wait_for_pdf_upload, convert_and_save, upload, cleanup
from dotenv import load_dotenv
import os
import json

def file_transform_handler(event, context):
    cwd = os.getcwd()
    
    try: 
        load_dotenv()
        body = event['body']
        FOLDER_NAME = json.loads(body)['folderName']

        ACCESS_KEY_ID=os.environ['ACCESS_KEY_ID']
        SECRET_ACCESS_KEY=os.environ['SECRET_ACCESS_KEY']
        BUCKET_NAME=os.environ['BUCKET_NAME']
        
        s3 = boto3.client(
            's3',
            aws_access_key_id=ACCESS_KEY_ID,
            aws_secret_access_key=SECRET_ACCESS_KEY
        )

        cloud_pdf_path = wait_for_pdf_upload(BUCKET_NAME, s3, FOLDER_NAME)
        print('cloud_pdf_path worked: ', cloud_pdf_path)
        local_pdf = f'{cwd}/uploaded.pdf'
        # download file from s3 to local, with name from local_pdf
        print('local_pdf: ', local_pdf)
        s3.download_file(BUCKET_NAME, cloud_pdf_path, local_pdf)
        print('download_file worked')

        image_paths = convert_and_save(local_pdf)
        print('image paths worked')
        cloud_image_paths = upload(BUCKET_NAME, s3, FOLDER_NAME, image_paths)
        print('cloud_image_paths worked')
        cleanup(local_pdf, image_paths) 
        print('cleanup worked')

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
    