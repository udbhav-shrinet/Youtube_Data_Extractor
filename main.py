import base64
import requests
from datetime import datetime
import os
import functions_framework
import json
import pandas as pd
from google.cloud import storage, bigquery
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Load configuration from JSON file
with open('config.json', 'r') as f:
    config = json.load(f)

# Extract configuration variables
api_key = config['api_key']
channel_ids = config['channel_ids']
project_id = config['project_id']
dataset_name = config['dataset_name']
table_name = config['table_name']
bucket_name = config['bucket_name']
credentials_file = config['credentials_file']

# Set environment variable for credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_file

# Initialize clients
bq_client = bigquery.Client(project=project_id)
gcs_client = storage.Client()

# Function to fetch live videos, export to CSV, upload to GCS, and load into BigQuery
@functions_framework.cloud_event
def hello_pubsub(cloud_event):
    event_data = base64.b64decode(event["data"]).decode('utf-8')
    print(f"Received event: {event_data}")
    fetch_youtube_live_videos_to_bigquery()

def fetch_youtube_live_videos_to_bigquery():
    for channel_id in channel_ids:
        page_token = ''
        videos_data = []
        while True:
            api_url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&eventType=live&type=video&channelId={channel_id}&key={api_key}&pageToken={page_token}&maxResults=50'
            try:
                response = requests.get(api_url)
                data = response.json()
                if 'items' in data:
                    videos_data.extend(data['items'])
                if 'nextPageToken' in data:
                    page_token = data['nextPageToken']
                else:
                    break
            except Exception as e:
                print(f'Error fetching data: {str(e)}')
                break
        
        if not videos_data:
            print(f"No data retrieved for channel ID: {channel_id}")
            continue

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

        print(f"Collected rows: {rows}")

        if not rows:
            print(f"No rows to write for channel ID: {channel_id}")
            continue

        df = pd.DataFrame(rows)
        csv_filename = f'temp_live_videos_{channel_id}.csv'
        df.to_csv(csv_filename, index=False)

        upload_to_gcs(csv_filename)
        os.remove(csv_filename)
        load_csv_to_bigquery(csv_filename)

def get_current_viewers(video_id):
    live_stats_url = f'https://www.googleapis.com/youtube/v3/videos?part=liveStreamingDetails&id={video_id}&key={api_key}'
    stats_response = requests.get(live_stats_url)
    stats_data = stats_response.json()
    try:
        return stats_data['items'][0]['liveStreamingDetails']['concurrentViewers']
    except (IndexError, KeyError):
        print(f"Error fetching current viewers for video ID: {video_id}")
        return None

def get_channel_name(channel_id):
    channel_url = f'https://www.googleapis.com/youtube/v3/channels?part=snippet&id={channel_id}&key={api_key}'
    channel_response = requests.get(channel_url)
    channel_data = channel_response.json()
    try:
        return channel_data['items'][0]['snippet']['title']
    except (IndexError, KeyError):
        print(f"Error fetching channel name for channel ID: {channel_id}")
        return None

def upload_to_gcs(filename):
    bucket = gcs_client.bucket(bucket_name)
    blob = bucket.blob(filename)
    blob.upload_from_filename(filename)
    print(f'File {filename} uploaded to GCS bucket {bucket_name}.')

def load_csv_to_bigquery(csv_filename):
    dataset_ref = bq_client.dataset(dataset_name)
    table_ref = dataset_ref.table(table_name)
    job_config = bigquery.LoadJobConfig()
    job_config.source_format = bigquery.SourceFormat.CSV
    job_config.skip_leading_rows = 1
    job_config.autodetect = True
    uri = f'gs://{bucket_name}/{csv_filename}'
    load_job = bq_client.load_table_from_uri(uri, table_ref, job_config=job_config)
    load_job.result()
    print(f'CSV data from {uri} loaded into BigQuery table {table_name}.')
    delete_from_gcs(csv_filename)

def delete_from_gcs(filename):
    bucket = gcs_client.bucket(bucket_name)
    blob = bucket.blob(filename)
    blob.delete()
    print(f'File {filename} deleted from GCS bucket {bucket_name}.')

if __name__ == "__main__":
    event = {
        'data': base64.b64encode(json.dumps({
            'channel_ids': channel_ids
        }).encode('utf-8')).decode('utf-8')
    }
    context = {}
    hello_pubsub(event)
