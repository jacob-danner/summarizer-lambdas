import asyncio
import aioboto3
from dotenv import load_dotenv
import os
import json
import logging

from parse_request import convert_to_dt
from download_utils import download_all_pages
from crop_utils import crop_all
from extract_text import extract_all_text


logging.getLogger().setLevel(logging.INFO)

async def async_handler(event, context):
    logging.debug(f'Event: {event}')
    
    load_dotenv()
    ACCESS_KEY_ID=os.environ['ACCESS_KEY_ID']
    SECRET_ACCESS_KEY=os.environ['SECRET_ACCESS_KEY']
    BUCKET_NAME=os.environ['BUCKET_NAME']

    # parse lambda request event into dataclasses
    body = event['body']
    allPages = json.loads(body)['allPages']
    req = convert_to_dt(allPages)
    
    try: 
        # download images. image_paths is only stored for logging
        image_paths = await download_all_pages(req, ACCESS_KEY_ID, SECRET_ACCESS_KEY, BUCKET_NAME)

        # crop images
        crop_all(req)
        print('cropped successfully')
        
        # TODO EVENTUALLY upload cropped images to s3 for ml.

        # extract text from each image
        all_text = extract_all_text()

        # pass text to summarizer
        
        
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
            "body": json.dumps(image_paths)
        }

    except Exception as e:
        return {
            "statusCode": 400,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            "body": f"{e}"
        }
    
    

def lambda_handler(event, context):
    loop = asyncio.get_event_loop()    
    return loop.run_until_complete(async_handler(event, context))