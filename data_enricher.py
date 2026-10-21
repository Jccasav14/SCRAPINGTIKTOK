import os
import sys
import json
import math
import argparse
import logging
from typing import Dict, Any, List, Optional
import requests

BENFORD_THEORETICAL = {
    1: math.log10(1 + 1 / 1),
    2: math.log10(1 + 1 / 2),
    3: math.log10(1 + 1 / 3),
    4: math.log10(1 + 1 / 4),
    5: math.log10(1 + 1 / 5),
    6: math.log10(1 + 1 / 6),
    7: math.log10(1 + 1 / 7),
    8: math.log10(1 + 1 / 8),
    9: math.log10(1 + 1 / 9),
}

def extract_numbers_from_data(data: Dict[str, Any]) -> List[int]:
    numbers = []
    for key in ["followers_count", "following_count", "heart_count", "video_count"]:
        val = data.get(key)
        if isinstance(val, (int, float)) and val >= 10:
            numbers.append(int(val))
    return numbers
