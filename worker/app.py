import json
import time
import boto3
from botocore.exceptions import ClientError
from loguru import logger
from utils import search_download_youtube_video


with open('config.json') as f:
    config = json.load(f)

sqs = boto3.resource('sqs', region_name=config.get('aws_region'))
queue = sqs.get_queue_by_name(
    QueueName=config.get('bot_to_worker_queue_name')
)


def process_msg(msg):
    # TODO upload the downloaded video to your S3 bucket
    video = search_download_youtube_video(msg)
    client = boto3.client("s3")
    client.upload_file(video[0]['filename'], "ao-bt", video[0]['filename'])

def main():
    while True:
        try:
            messages = queue.receive_messages(
                MessageAttributeNames=['All'],
                MaxNumberOfMessages=1,
                WaitTimeSeconds=10
            )
            for msg in messages:
                logger.info(f'processing message {msg}')
                process_msg(msg.body)

                # delete message from the queue after is was handled
                response = queue.delete_messages(Entries=[{
                    'Id': msg.message_id,
                    'ReceiptHandle': msg.receipt_handle
                }])
                if 'Successful' in response:
                    logger.info(f'msg {msg} has been handled successfully')

        except ClientError as err:
            logger.exception(f"Couldn't receive messages {err}")
            time.sleep(10)


def lambda_handler(event, context):
    logger.info(f'New event {event}')

    for record in event['Records']:
        process_msg(str(record["body"]))


if __name__ == '__main__':
    main()
