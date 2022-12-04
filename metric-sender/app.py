import boto3
import json
from loguru import logger
import os

with open('common/config.json') as f:
    config = json.load(f)


bot_to_worker_queue_name = config.get('bot_to_worker_queue_name')
autoscaling_group_name = config.get('autoscaling_group_name')

sqs = boto3.resource('sqs')
workers_queue = sqs.get_queue_by_name(QueueName=bot_to_worker_queue_name)
asg_client = boto3.client('autoscaling')


def calc_backlog_per_instance():
    msgs_in_queue = int(workers_queue.attributes.get('ApproximateNumberOfMessages'))
    asg_groups = asg_client.describe_auto_scaling_groups(AutoScalingGroupNames=[autoscaling_group_name])['AutoScalingGroups']

    if not asg_groups:
        raise RuntimeError('Autoscaling group not found')
    else:
        asg_size = asg_groups[0]['DesiredCapacity']

    if msgs_in_queue == 0:
        backlog_per_instance = 0
    elif asg_size == 0:
        backlog_per_instance = 99
    else:
        backlog_per_instance = msgs_in_queue / asg_size

    return backlog_per_instance


def lambda_handler(event, context):
    backlog_per_instance = calc_backlog_per_instance()
    logger.info(f'backlog per instance: {backlog_per_instance}')

    # TODO send the backlog_per_instance metric to cloudwatch


# For debug purposes -this below expression is True only if the code runs locally, not in AWS Lambda function
if os.environ.get("AWS_EXECUTION_ENV") is not None:
    lambda_handler(None, None)
