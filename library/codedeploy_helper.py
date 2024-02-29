import boto3
import time

# Initialize the CodeDeploy client outside the function if you're using it across multiple functions
codedeploy_client = boto3.client('codedeploy')

def list_recent_deployments(application_name, deployment_group_name, invocation_time, look_forward=600):
    """
    List recent deployments for the given application name and deployment group, starting from the invocation time.
    :param application_name: The name of the CodeDeploy application.
    :param deployment_group_name: The name of the deployment group in the application.
    :param invocation_time: The datetime object representing when the Lambda was invoked.
    :param look_forward: The time in seconds to look forward from the invocation time for deployments.
    :return: A list of deployment IDs.
    """
    # Convert invocation_time to epoch time
    start_time_epoch = int(invocation_time.timestamp())

    deployments = codedeploy_client.list_deployments(
        applicationName=application_name,
        deploymentGroupName=deployment_group_name,
        createTimeRange={
            'start': start_time_epoch,
            'end': start_time_epoch + look_forward
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

def monitor_deployments(application_name, deployment_group_name, invocation_time, polling_interval=30, max_attempts=20):
    """
    Monitors the deployments for the specified application and deployment group, polling every `polling_interval` seconds, starting from the invocation time.
    
    :param application_name: The name of the CodeDeploy application.
    :param deployment_group_name: The name of the deployment group within the application.
    :param invocation_time: The datetime object representing when the Lambda was invoked.
    :param polling_interval: The interval, in seconds, between each status check.
    :param max_attempts: The maximum number of polling attempts before giving up.
    :return: Tuple (bool, str) indicating success/failure and status message.
    """
    attempts = 0
    while attempts < max_attempts:
        deployments = list_recent_deployments(application_name, deployment_group_name, invocation_time=invocation_time)
        if not deployments:
            print("No recent deployments found since invocation time. Waiting before checking again.")
            time.sleep(polling_interval)
            attempts += 1
            continue

        all_deployments_final = True
        any_deployment_failed = False

        for deployment_id in deployments:
            status = check_deployment_status(deployment_id)
            if status in ['Failed', 'Stopped']:
                print(f"Deployment {deployment_id} failed or stopped with status: {status}")
                any_deployment_failed = True
                break  # No need to check further, as we already encountered a failure
            elif status not in ['Succeeded']:
                all_deployments_final = False

        if any_deployment_failed:
            return False, "Failed"  # Indicates a deployment failed or stopped

        if all_deployments_final:
            return True, "Succeeded"  # All deployments succeeded

        # If not all deployments are final or any have failed, continue polling
        print(f"Deployments are still in progress. Attempting again in {polling_interval} seconds.")
        time.sleep(polling_interval)
        attempts += 1

    return False, "Timeout"  # Not all deployments succeeded within the allowed attempts
