import aioboto3
import asyncio
import os
from typing import List
from dotenv import load_dotenv
import time

import data_types as dt

async def _download_single_page(imageURL: str, s3_client: aioboto3.Session.client, BUCKET_NAME) -> str:
    '''
    download page image from s3 bucket and save locally

    input: url to page image in s3 bucket
    return: path to downloaded image

    private method
    '''
    
    url_split = imageURL.split('/')            # ex: '...s3.amazonaws.com/04578765-95db-4124-b8d9-fbbab636786d/tmp/1.jpg'
    s3_obj_name = '/'.join( url_split[-3:] )   # ex: -> '04578765-95db-4124-b8d9-fbbab636786d/tmp/1.jpg'
    img_id =      url_split[-1]                # ex: -> '1.jpg'
    local_path = f'/tmp/{img_id}'

    try:
        await s3_client.download_file(BUCKET_NAME, s3_obj_name, local_path)
    except Exception as e:
         print(f'Error in download_page_img: An error occured trying to download the PDF from S3: {e}')
    
    return local_path



async def download_all_pages(req: dt.Request, ACCESS_KEY_ID, SECRET_ACCESS_KEY, BUCKET_NAME) -> List[str]:
    '''
    with async client, create coroutines to download each page. run all coroutines, downloading all page images

    input: request (parsed into dataclass), aws secrets
    output: List[local_path_image]

    public method
    '''
    start = time.time()

    session = aioboto3.Session()
    async with session.client(
        's3',
        aws_access_key_id=ACCESS_KEY_ID,
        aws_secret_access_key=SECRET_ACCESS_KEY
    ) as s3_client:
        tasks = [_download_single_page(page.imageURL, s3_client, BUCKET_NAME) for page in req]
        local_paths = await asyncio.gather(*tasks)
        end = time.time()
        print(f'downloaded {len(local_paths)} images in {end - start} seconds')
        return local_paths