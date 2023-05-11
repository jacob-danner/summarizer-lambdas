from data_types import Request, Box, Page
from typing import List, Dict

def convert_to_dt(lambda_event: List[Dict]) -> Request:
    '''
    input: lambda event that's been json.loads() into a list of dicts
    returns: input parsed into Request datatype
    '''
    req: Request = []
    for obj in lambda_event:
        pageNum = obj['pageNum']
        imageURL = obj['imageURL']
        boxes: List[Box] = []
        for b in obj['boxes']:
            x = b['x']
            y = b['y']
            w = b['w']
            h = b['h']
            box = Box(x, y, w, h)
            boxes.append(box)

        page = Page(pageNum, imageURL, boxes)
        req.append(page)

    return req
    