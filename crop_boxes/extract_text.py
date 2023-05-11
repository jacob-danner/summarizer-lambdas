import pytesseract
from PIL import Image
import os
from typing import List

def extract_all_text() -> List[str]:
    '''
    for each cropped image located in /tmp/cropped, extract the text. compile each pages text into a list
    
    input: None
    returns: List[extracted_text] 
    '''

    cropped_dir_path = '/tmp/cropped'

    image_paths = sorted(os.listdir(cropped_dir_path))
    all_text = [ pytesseract.image_to_string( Image.open( f'{cropped_dir_path}/{img}' ) ) for img in image_paths]
    return all_text