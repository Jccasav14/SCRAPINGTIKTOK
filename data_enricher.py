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

    for follower in data.get("followers_list", []):
        f_count = follower.get("followers_count")
        if isinstance(f_count, (int, float)) and f_count >= 10:
            numbers.append(int(f_count))
        fg_count = follower.get("following_count")
        if isinstance(fg_count, (int, float)) and fg_count >= 10:
            numbers.append(int(fg_count))

    for following in data.get("following_list", []):
        f_count = following.get("followers_count")
        if isinstance(f_count, (int, float)) and f_count >= 10:
            numbers.append(int(f_count))

    for video in data.get("videos", []):
        for v_key in ["likes_count", "comments_count", "views_count", "shares_count", "bookmarks_count"]:
            val = video.get(v_key)
            if isinstance(val, (int, float)) and val >= 10:
                numbers.append(int(val))

        for comment in video.get("comments", []):
            c_likes = comment.get("likes_count")
            if isinstance(c_likes, (int, float)) and c_likes >= 10:
                numbers.append(int(c_likes))

    return numbers

# first-digit parsing
