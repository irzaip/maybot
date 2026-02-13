"""Media encoding utilities for WhatsApp responses - Backend module"""

import base64
import json
import os
from typing import List, Dict, Optional

MAX_SIZE_BYTES = 10 * 1024 * 1024  # 10MB


def make_media_response(text: str, attachments: List[Dict] = None) -> Dict:
    """Build WhatsApp response with text and base64 attachments."""
    content = {"text": text}
    if attachments:
        content["attachments"] = attachments
    return {"message": json.dumps(content)}


def encode_file(file_path: str, mimetype: str, filename: str) -> Optional[Dict]:
    """Read file from disk, check size, encode to base64."""
    if not os.path.exists(file_path):
        return None
    size = os.path.getsize(file_path)
    if size > MAX_SIZE_BYTES:
        return None
    with open(file_path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    return {"type": "file", "mimetype": mimetype, "data": data, "filename": filename}


def encode_relative(relative_path: str, mimetype: str, filename: str) -> Optional[Dict]:
    """Encode file from media/ directory."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_path = os.path.join(base_dir, "media", relative_path)
    return encode_file(full_path, mimetype, filename)
