import boto3
from pdf2image import convert_from_path
import os

# def check_bucket_permission(s3_client, bucket_name):
#     try:
#         # Use head_bucket to check if the bucket exists and if we have permission to access it
#         response = s3_client.head_bucket(Bucket=bucket_name)
#         print("Bucket exists and we have permission to access it")
#         return True
#     except s3_client.exceptions.ClientError as e:
#         # Check if the error is related to bucket not existing or permissions
#         error_code = int(e.response['Error']['Code'])
#         if error_code == 403:
#             print("We do not have permission to access the bucket")
#         elif error_code == 404:
#             print("Bucket does not exist")
#         else:
#             print("Unexpected error: {}".format(e))
#         return False
    
    
def wait_for_pdf_upload(bucket_name, s3_client: boto3.client, folder_name: str) -> str:
    # wait for uploaded.pdf to exist in the bucket, at folder/uploaded.pdf path
    # return the path to the pdf file so it can be downloaded
    try:
        cloud_pdf_key = f'{folder_name}/uploaded.pdf'
        waiter = s3_client.get_waiter('object_exists')
        waiter.wait(Bucket=bucket_name, Key=cloud_pdf_key)
        return cloud_pdf_key

    except:
        print('issue finding the pdf @ wait_for_pdf_upload')
        return None

        
def convert_and_save(pdf_path: str) -> str:
    # convert pdf to images, return list of filenames
    file_names = []
    images = convert_from_path(pdf_path)
    for i, img in enumerate(images):
        f_name = f'{str(i)}.jpg'
        file_names.append(f_name)
        img.save(f_name)

    return file_names


def upload(bucket_name, s3, folder_name, image_paths):
    # upload, return list of image paths as in s3 bucket
    cloud_image_paths = []
    for local_img_file in image_paths:
        cloud_image_path = f'{folder_name}{local_img_file}'
        cloud_image_paths.append()
        s3.upload_file(local_img_file, bucket_name, cloud_image_path)
    
    return cloud_image_paths


def cleanup(pdf, image_paths):
    files = [pdf]
    files.extend(image_paths)
    for file in files:
        os.remove(file)