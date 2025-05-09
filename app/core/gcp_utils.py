# app/core/gcp_utils.py

import os
from google.cloud import storage

def upload_to_gcs(file_obj, destination_blob_name):
    bucket_name = os.getenv("GCP_BUCKET_NAME")
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_file(file_obj, rewind=True)
    return f"gs://{bucket_name}/{destination_blob_name}"
