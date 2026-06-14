import os
import boto3
from botocore.config import Config
from typing import List, Dict, Optional, BinaryIO
from datetime import datetime
import mimetypes

from shared.constants import (
    R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY,
    R2_BUCKET, R2_PUBLIC_URL, UPLOADS_PREFIX, STATE_KEY,
    PRESIGNED_URL_EXPIRY, PRESIGNED_URL_MAX_SIZE, ALLOWED_EXTENSIONS
)

_client = None

def get_r2_client():
    global _client
    if _client is None:
        _client = boto3.client(
            "s3",
            endpoint_url=f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
            aws_access_key_id=R2_ACCESS_KEY_ID,
            aws_secret_access_key=R2_SECRET_ACCESS_KEY,
            config=Config(signature_version="s3v4"),
            region_name="auto",
        )
    return _client

def get_bucket_name() -> str:
    return R2_BUCKET

def list_files(prefix: str = UPLOADS_PREFIX) -> List[Dict]:
    """List all files in bucket with given prefix."""
    client = get_r2_client()
    paginator = client.get_paginator("list_objects_v2")
    files = []
    for page in paginator.paginate(Bucket=R2_BUCKET, Prefix=prefix):
        for obj in page.get("Contents", []):
            files.append({
                "name": obj["Key"].replace(prefix, ""),
                "key": obj["Key"],
                "size": obj["Size"],
                "mtime": obj["LastModified"].isoformat(),
                "etag": obj.get("ETag", "").strip('"'),
            })
    return sorted(files, key=lambda x: x["mtime"], reverse=True)

def get_file_metadata(key: str) -> Optional[Dict]:
    """Get metadata for a single file."""
    client = get_r2_client()
    try:
        response = client.head_object(Bucket=R2_BUCKET, Key=key)
        return {
            "key": key,
            "size": response["ContentLength"],
            "mtime": response["LastModified"].isoformat(),
            "content_type": response.get("ContentType"),
            "etag": response.get("ETag", "").strip('"'),
        }
    except client.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return None
        raise

def generate_presigned_put_url(filename: str, content_type: str = None) -> Dict:
    """Generate presigned PUT URL for direct client upload."""
    client = get_r2_client()
    key = f"{UPLOADS_PREFIX}{filename}"
    
    if content_type is None:
        content_type, _ = mimetypes.guess_type(filename)
        if content_type is None:
            content_type = "application/octet-stream"
    
    url = client.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": R2_BUCKET,
            "Key": key,
            "ContentType": content_type,
        },
        ExpiresIn=300,  # 5 minutes
    )
    
    return {
        "uploadUrl": url,
        "fileKey": key,
        "filename": filename,
        "expiresIn": 300,
        "method": "PUT",
        "headers": {"Content-Type": content_type},
    }

def generate_presigned_get_url(key: str, expires_in: int = 3600) -> str:
    """Generate presigned GET URL for file access."""
    client = get_r2_client()
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": R2_BUCKET, "Key": key},
        ExpiresIn=expires_in,
    )

def delete_file(key: str) -> bool:
    """Delete a file from R2."""
    client = get_r2_client()
    try:
        client.delete_object(Bucket=R2_BUCKET, Key=key)
        return True
    except client.exceptions.ClientError:
        return False

def get_state() -> List[str]:
    """Get uploaded files state from R2."""
    client = get_r2_client()
    try:
        response = client.get_object(Bucket=R2_BUCKET, Key=STATE_KEY)
        import json
        return json.loads(response["Body"].read())
    except client.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return []
        raise

def save_state(files: List[str]) -> None:
    """Save uploaded files state to R2."""
    client = get_r2_client()
    import json
    client.put_object(
        Bucket=R2_BUCKET,
        Key=STATE_KEY,
        Body=json.dumps(files).encode(),
        ContentType="application/json",
    )

def get_new_files() -> List[str]:
    """Get files not in state."""
    all_files = [f["name"] for f in list_files()]
    state = set(get_state())
    return [f for f in all_files if f not in state]

def add_to_state(filename: str) -> None:
    """Add filename to state."""
    state = get_state()
    if filename not in state:
        state.append(filename)
        save_state(state)

def file_exists(key: str) -> bool:
    """Check if file exists in R2."""
    client = get_r2_client()
    try:
        client.head_object(Bucket=R2_BUCKET, Key=key)
        return True
    except client.exceptions.ClientError:
        return False

def get_public_url(key: str) -> str:
    """Get public URL for file (if bucket is public)."""
    if R2_PUBLIC_URL:
        return f"{R2_PUBLIC_URL.rstrip('/')}/{key}"
    return f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com/{R2_BUCKET}/{key}"

def validate_file(filename: str, size: int = None) -> Optional[str]:
    """Validate file extension and size. Returns error message if invalid."""
    import os
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return f"Invalid extension: {ext}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
    if size and size > PRESIGNED_URL_MAX_SIZE:
        return f"File too large: {size} bytes (max {PRESIGNED_URL_MAX_SIZE})"
    return None