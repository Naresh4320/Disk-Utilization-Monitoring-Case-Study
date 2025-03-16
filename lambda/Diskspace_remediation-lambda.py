import boto3
import json
import os
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize clients
ssm = boto3.client('ssm')
cloudwatch = boto3.client('cloudwatch')
sts = boto3.client('sts')

# Environment variables
TARGET_ROLE_ARN_PREFIX = os.environ['TARGET_ROLE_ARN_PREFIX']
SSM_DOCUMENT_NAME = os.environ['SSM_DOCUMENT_NAME']
LOG_CLEANUP_PATHS = os.environ.get('LOG_CLEANUP_PATHS', '/var/log/')

def assume_role(account_id):
    """Assume the appropriate role for the target account"""
    role_arn = f"{TARGET_ROLE_ARN_PREFIX}{account_id}"
    logger.info(f"Assuming role: {role_arn}")
    
    assumed_role = sts.assume_role(
        RoleArn=role_arn,
        RoleSessionName=f"DiskRemediationSession-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    )
    
    credentials = assumed_role['Credentials']
    return boto3.Session(
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken']
    )

def lambda_handler(event, context):
    """Handle CloudWatch alarm events for disk utilization"""
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Parse the CloudWatch alarm event
        alarm_data = event['detail']
        instance_id = alarm_data['configuration']['metrics'][0]['metricStat']['metric']['dimensions']['InstanceId']
        account_id = alarm_data['accountId']
        alarm_name = alarm_data['alarmName']
        alarm_threshold = float(alarm_data['configuration']['threshold'])
        current_value = float(alarm_data['state']['value'])
        
        logger.info(f"Processing alarm {alarm_name} for instance {instance_id} in account {account_id}")
        logger.info(f"Current value: {current_value}%, threshold: {alarm_threshold}%")
        
        # Determine remediation level based on threshold
        if alarm_threshold >= 95:
            remediation_level = "critical"
        elif alarm_threshold >= 85:
            remediation_level = "high"
        else:
            remediation_level = "medium"
        
        # Assume role in target account
        target_session = assume_role(account_id)
        target_ssm = target_session.client('ssm')
        
        # Execute appropriate remediation based on severity
        if remediation_level == "critical":
            # Critical: Run emergency cleanup and notify
            response = target_ssm.send_command(
                InstanceIds=[instance_id],
                DocumentName=SSM_DOCUMENT_NAME,
                Parameters={
                    'action': ['emergency_cleanup'],
                    'paths': [LOG_CLEANUP_PATHS]
                },
                Comment=f"Emergency disk cleanup triggered by {alarm_name}"
            )
        elif remediation_level == "high":
            # High: Run standard cleanup
            response = target_ssm.send_command(
                InstanceIds=[instance_id],
                DocumentName=SSM_DOCUMENT_NAME,
                Parameters={
                    'action': ['standard_cleanup'],
                    'paths': [LOG_CLEANUP_PATHS]
                },
                Comment=f"Standard disk cleanup triggered by {alarm_name}"
            )
        else:
            # Medium: Run log rotation only
            response = target_ssm.send_command(
                InstanceIds=[instance_id],
                DocumentName=SSM_DOCUMENT_NAME,
                Parameters={
                    'action': ['log_rotation'],
                    'paths': [LOG_CLEANUP_PATHS]
                },
                Comment=f"Log rotation triggered by {alarm_name}"
            )
        
        command_id = response['Command']['CommandId']
        logger.info(f"Initiated remediation command {command_id} for instance {instance_id}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f"Remediation initiated for instance {instance_id}",
                'command_id': command_id,
                'remediation_level': remediation_level
            })
        }
    
    except Exception as e:
        logger.error(f"Error processing event: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f"Error: {str(e)}"
            })
        }
