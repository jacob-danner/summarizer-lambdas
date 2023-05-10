from dataclasses import dataclass
from typing import List

@dataclass
class Box:
    x: int
    y: int
    w: int
    h: int

@dataclass
class Page:
    pageNum: int
    imageURL: str
    boxes: List[Box]

@dataclass
class Request:
    List[Page]