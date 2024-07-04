import base64
import requests
from datetime import datetime, timedelta
from google.cloud import storage
import os
import functions_framework
import random
import json
import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.cloud import bigquery

# Set your YouTube API key
api_key = 'yourapikey'

# Set the YouTube channel IDs for which you want to fetch live videos
channel_ids = [yourchannelids]

# BigQuery configuration
project_id = 'yrprojectid'
dataset_id = 'yourdatasetid'
table_id = 'yourtableid'

# Google Cloud Storage configuration
bucket_name = 'yourbucketname'
csv_filename = 'temp_live_videos.csv'

# Set environment variable for credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'yourjsonfilecreds.json'

# Initialize BigQuery client
bq_client = bigquery.Client(project=project_id)

# Initialize Google Cloud Storage client
gcs_client = storage.Client()

# Triggered from a message on a Cloud Pub/Sub topic.
@functions_framework.cloud_event
def hello_pubsub(cloud_event):
    event_data = base64.b64decode(cloud_event.data["message"]["data"]).decode('utf-8')
    print(f"Received event: {event_data}")
    fetch_youtube_live_videos_to_bigquery()

# Function to fetch live videos from YouTube API, export to CSV, upload to GCS, and load into BigQuery
def fetch_youtube_live_videos_to_bigquery():
    for channel_id in channel_ids:
        page_token = ''
        videos_data = []
        while True:
            # API endpoint to fetch live videos with pagination
            api_url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&eventType=live&type=video&channelId={channel_id}&key={api_key}&pageToken={page_token}&maxResults=50'
            
            # Fetch data from YouTube API
            try:
                response = requests.get(api_url)
                data = response.json()
                if 'items' in data:
                    videos_data.extend(data['items'])
                if 'nextPageToken' in data:
                    page_token = data['nextPageToken']
                else:
                    break  # Exit loop if there are no more pages
            except Exception as e:
                print(f'Error fetching data: {str(e)}')
                break  # Exit loop on error
        
        if not videos_data:
            print(f"No data retrieved for channel ID: {channel_id}")
            continue  # Skip to the next channel ID if no data is retrieved

        # Prepare data for CSV
        rows = []
        for video in videos_data:
            try:
                video_id = video['id']['videoId']
                video_title = video['snippet']['title']
                current_viewers = get_current_viewers(video_id)
                channel_name = get_channel_name(channel_id)
                current_date = datetime.utcnow()
                formatted_date = current_date.strftime('%Y-%m-%d %H:%M')
                rows.append({
                    'video_title': video_title,
                    'video_id': video_id,
                    'channel_name': channel_name,
                    'current_viewers': current_viewers,
                    'datetime': formatted_date
                })
            except Exception as e:
                print(f"Error processing video data: {str(e)}")

        # Log the collected rows
        print(f"Collected rows: {rows}")

        # Check if rows are not empty
        if not rows:
            print(f"No rows to write for channel ID: {channel_id}")
            continue  # Skip to the next channel ID if no rows are collected

        # Convert to DataFrame
        df = pd.DataFrame(rows)

        # Export DataFrame to CSV
        df.to_csv(csv_filename, index=False)

        # Upload CSV file to Google Cloud Storage
        upload_to_gcs(csv_filename)

        # Clean up: Remove local CSV file
        os.remove(csv_filename)

        # Load CSV data to BigQuery
        load_csv_to_bigquery()

def get_current_viewers(video_id):
    # Fetch current viewer count for a video using YouTube API
    live_stats_url = f'https://www.googleapis.com/youtube/v3/videos?part=liveStreamingDetails&id={video_id}&key={api_key}'
    stats_response = requests.get(live_stats_url)
    stats_data = stats_response.json()
    try:
        return stats_data['items'][0]['liveStreamingDetails']['concurrentViewers']
    except (IndexError, KeyError):
        print(f"Error fetching current viewers for video ID: {video_id}")
        return None

def get_channel_name(channel_id):
    # Fetch channel name using YouTube API
    channel_url = f'https://www.googleapis.com/youtube/v3/channels?part=snippet&id={channel_id}&key={api_key}'
    channel_response = requests.get(channel_url)
    channel_data = channel_response.json()
    try:
        return channel_data['items'][0]['snippet']['title']
    except (IndexError, KeyError):
        print(f"Error fetching channel name for channel ID: {channel_id}")
        return None

def upload_to_gcs(filename):
    # Upload file to Google Cloud Storage bucket
    bucket = gcs_client.bucket(bucket_name)
    blob = bucket.blob(filename)
    blob.upload_from_filename(filename)

    print(f'File {filename} uploaded to GCS bucket {bucket_name}.')

def load_csv_to_bigquery():
    # Load CSV file from GCS to BigQuery
    dataset_ref = bq_client.dataset(dataset_id)
    table_ref = dataset_ref.table(table_id)

    job_config = bigquery.LoadJobConfig()
    job_config.source_format = bigquery.SourceFormat.CSV
    job_config.skip_leading_rows = 1
    job_config.autodetect = True

    uri = f'gs://{bucket_name}/{csv_filename}'

    load_job = bq_client.load_table_from_uri(
        uri, table_ref, job_config=job_config
    )
    load_job.result()  # Waits for the job to complete.

    print(f'CSV data from {uri} loaded into BigQuery table {table_id}.')

    # Delete the CSV file from GCS
    delete_from_gcs(csv_filename)

def delete_from_gcs(filename):
    # Delete file from Google Cloud Storage bucket
    bucket = gcs_client.bucket(bucket_name)
    blob = bucket.blob(filename)
    blob.delete()

    print(f'File {filename} deleted from GCS bucket {bucket_name}.')

if __name__ == "__main__":
    # Sample event data for local testing
    event = {
        'data': base64.b64encode(json.dumps({
            'channel_ids': ["UCRWFSbif-RFENbBrSiez1DA"]  # Add your channel IDs here
        }).encode('utf-8')).decode('utf-8')
    }
    context = {}  # Context is not used in this example

    hello_pubsub(event)
