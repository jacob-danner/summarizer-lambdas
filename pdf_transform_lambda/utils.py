import aioboto3
import asyncio
import boto3
from pdf2image import convert_from_path
from PIL.Image import Image
from typing import List
import os
import logging

logger = logging.getLogger(__name__)

async def wait_for_pdf_upload(bucket_name: str, s3_client: aioboto3.Session.client, folder_name: str) -> str:
    '''
    wait for uploaded.pdf to exist in the bucket, at folder/uploaded.pdf path
    return the path to the pdf file so it can be downloaded
    '''

    logger.debug(f'wait_for_pdf_upload(): bucket_name: {bucket_name}, s3_client: {s3_client}, folder_name: {folder_name}')

    try:
        cloud_pdf_key = f'{folder_name}/uploaded.pdf'
        waiter = s3_client.get_waiter('object_exists')
        await waiter.wait(Bucket=bucket_name, Key=cloud_pdf_key, WaiterConfig={'Delay': 1, 'MaxAttempts': 3})

        logger.info(f'S3 PDF Key: {cloud_pdf_key}')
        return cloud_pdf_key

    except Exception as e:
        logger.error(f'error @ wait_for_pdf_upload(): {e}')
        raise e

        
def convert_and_save(pdf_path: str) -> str:
    '''
    convert pdf to images, 
    download PIL images to /tmp,
    return list of filenames
    '''

    logger.debug(f'convert_and_save(): pdf_path: {pdf_path}')

    file_names = []
    images: List[Image] = convert_from_path(pdf_path)

    for i, img in enumerate(images):
        f_name = f'/tmp/{str(i)}.jpg'
        file_names.append(f_name)
        img = img.resize((1010, 1320))
        img.save(f_name)

    logger.info(f'image paths: {file_names}')
    return file_names


async def upload(bucket_name, s3_client, folder_name, image_paths):
    '''
    upload each image in image_paths,
    return list of image paths as in s3 bucket
    '''
    logger.debug(f'upload(): bucket_name: {bucket_name}, s3_client: {s3_client}, folder_name: {folder_name}, image_paths: {image_paths}')

    tasks = [] # async tasks
    cloud_image_paths = []
    for local_img_file in image_paths:
        cloud_image_path = f'{folder_name}{local_img_file}'
        cloud_image_paths.append(cloud_image_path)
        task = upload_one(s3_client, local_img_file, bucket_name, cloud_image_path)
        tasks.append(task)

    await asyncio.gather(*tasks)
    
    logger.info(f'cloud image paths: {cloud_image_paths}')
    return cloud_image_paths

    
async def upload_one(s3_client, local_img_file, bucket_name, cloud_image_path):
        try:
            await s3_client.upload_file(local_img_file, bucket_name, cloud_image_path)
        except Exception as e:
            print(f'Error in upload_one: An error occured trying to upload the image to s3: {e}')



def cleanup(pdf, image_paths):
    '''
    remove downloaded files from /tmp directory.
    needed in case of hot start
    '''

    logger.debug(f'cleanup(): pdf: {pdf}, image_paths: {image_paths}')

    files = [pdf]
    files.extend(image_paths)
    for file in files:
        os.remove(file)