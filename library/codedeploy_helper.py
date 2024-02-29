# library/codedeploy_helper.py
import boto3
import time

codedeploy_client = boto3.client('codedeploy')

def list_recent_deployments(application_name, deployment_group_name, time_frame=600):
    """
    List recent deployments for the given application name and deployment group within the specified time frame.
    :param application_name: The name of the CodeDeploy application.
    :param deployment_group_name: The name of the deployment group in the application.
    :param time_frame: The time frame in seconds to look back for recent deployments.
    :return: A list of deployment IDs.
    """
    now = int(time.time())
    deployments = codedeploy_client.list_deployments(
        applicationName=application_name,
        deploymentGroupName=deployment_group_name,
        createTimeRange={
            'start': now - time_frame,
            'end': now
        }
    )['deployments']
    return deployments

def check_deployment_status(deployment_id):
    """
    Check the status of a CodeDeploy deployment.
    :param deployment_id: The ID of the deployment to check.
    :return: The status of the deployment.
    """
    deployment_info = codedeploy_client.get_deployment(deploymentId=deployment_id)
    return deployment_info['deploymentInfo']['status']

def monitor_deployments(application_name, deployment_group_name, time_frame=1200, polling_interval=30, max_attempts=20):
    """
    Monitors the deployments for the specified application and deployment group, polling every `polling_interval` seconds.
    
    :param application_name: The name of the CodeDeploy application.
    :param deployment_group_name: The name of the deployment group within the application.
    :param time_frame: The time frame in seconds to consider for recent deployments.
    :param polling_interval: The interval, in seconds, between each status check.
    :param max_attempts: The maximum number of polling attempts before giving up.
    :return: True if all deployments succeeded, False otherwise.
    """
    deployments = list_recent_deployments(application_name, deployment_group_name, time_frame=time_frame)

    attempts = 0
    while attempts < max_attempts:
        all_deployments_succeeded = True
        for deployment_id in deployments:
            status = check_deployment_status(deployment_id)
            if status not in ['Succeeded', 'Failed', 'Stopped']:
                all_deployments_succeeded = False
                print(f"Waiting for deployment {deployment_id} to complete. Current status: {status}")
                break 

        if all_deployments_succeeded:
            return True

        time.sleep(polling_interval)
        attempts += 1
    return False