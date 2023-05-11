import os
from PIL import Image
from shutil import rmtree

from data_types import Request, Page, Box

def _save_single_crop(page_img_path: str, box: Box, output_img_path: str) -> None:
    '''
    input: path to page image, box to crop, path for cropped image to be saved to
    output: void 

    private method
    '''
    x, y, w, h = box.x, box.y, box.w, box.h

    with Image.open(page_img_path) as img:
        # box dimensions need scaled by 2 in order to match the web app dimensions to actual image dimension. 
        # web app operates on 510 x 660 pixels, whereas images are saved as 1020 x 1320 pixels
        x *= 2
        y *= 2
        w *= 2
        h *= 2
        
        cropped = img.crop( (x, y, x+w, y+h) ) # crop takes a tuple
        cropped.save(output_img_path)

def crop_all(req: Request) -> None:
    '''
    input: Request
    output: None
    
    public method
    for every page in request, and every box in page.boxes, crop and save the image to match the bounding box.
    '''
    cropped_dir_path = '/tmp/cropped'

    if os.path.exists(cropped_dir_path):
        print('removing')
        rmtree(cropped_dir_path) # clear it. this is in place to prevent possible issues with lambda hot starts where there might be leftover stuff
    os.mkdir(cropped_dir_path)
    
    for i, page in enumerate(req):
        page_img_path = f'/tmp/{page.pageNum}.jpg'
        for j, box in enumerate(page.boxes):
            output_path = f'{cropped_dir_path}/{page.pageNum}_{j}.jpg'
            _save_single_crop(page_img_path, box, output_path)