import boto3
import json
import logging
import os

AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')

# Configure the logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def get_codepipeline_client():
    """
    Returns a boto3 client for AWS CodePipeline.
    This function can be modified to dynamically set the region or other client parameters if needed.
    """
    return boto3.client('codepipeline', region_name=AWS_REGION)


def report_job_success(job_id):
    """
    Notify AWS CodePipeline of a successful job execution.
    :param job_id: The ID of the CodePipeline job
    """
    client = get_codepipeline_client()
    try:
        client.put_job_success_result(jobId=job_id)
        logger.debug(f"Job {job_id} reported as success.")
    except Exception as e:
        logger.debug(f"Error reporting job success for {job_id}: {str(e)}")


def report_job_failure(job_id, message):
    """
    Notify AWS CodePipeline of a failed job execution.
    :param job_id: The ID of the CodePipeline job
    :param message: The failure message to report back to CodePipeline
    """
    client = get_codepipeline_client()
    try:
        client.put_job_failure_result(
            jobId=job_id,
            failureDetails={'message': message, 'type': 'JobFailed'}
        )
        logger.debug(f"Job {job_id} reported as failure. Message: {message}")
    except Exception as e:
        logger.debug(f"Error reporting job failure for {job_id}: {str(e)}")


def approve_action(pipeline_name, stage_name, action_name, token):
    client = get_codepipeline_client()
    try:
        response = client.put_approval_result(
            pipelineName=pipeline_name,
            stageName=stage_name,
            actionName=action_name,
            result={
                'summary': 'Deployment successful, automatically approved by Lambda.',
                'status': 'Approved'
            },
            token=token
        )
        logger.debug(
            f"Approval submitted successfully for action {action_name} in stage "
            f"{stage_name} of pipeline {pipeline_name}: {response}"
        )

        return {'statusCode': 200, 'body': json.dumps('Approval submitted successfully.')}
    except Exception as e:
        logger.debug(f"Error submitting approval for action {action_name} in pipeline {pipeline_name}: {str(e)}")
        return {'statusCode': 500, 'body': json.dumps(f"Error processing approval: {str(e)}")}


def find_action_in_stage(stage, action_name):
    """
    Find an action by name in a given stage.
    :param stage: The stage dictionary
    :param action_name: The name of the action to find
    :return: The action dictionary if found, else None
    """
    for action in stage['actionStates']:
        if action['actionName'] == action_name:
            return action
    return None


def extract_token_if_available(action):
    """
    Extract the approval token from an action if it is available and the action is in progress.
    :param action: The action dictionary
    :return: The approval token if available and action is in progress, else None
    """
    latest_execution = action.get('latestExecution', {})
    if latest_execution.get('status') == 'InProgress' and 'token' in latest_execution:
        return latest_execution['token']
    return None


def get_approval_token(pipeline_name, stage_name, action_name):
    """
    Get the approval token for a specific action in a pipeline stage if it's available.
    :param pipeline_name: The name of the pipeline
    :param stage_name: The name of the stage
    :param action_name: The name of the action
    :return: The approval token if found, else None
    """
    client = get_codepipeline_client()
    try:
        pipeline_state = client.get_pipeline_state(name=pipeline_name)
    except Exception as e:
        logger.debug(f"Error getting pipeline state for {pipeline_name}: {str(e)}")
        return None

    for stage in pipeline_state['stageStates']:
        if stage['stageName'] != stage_name:
            continue

        action = find_action_in_stage(stage, action_name)
        if action:
            token = extract_token_if_available(action)
            if token:
                logger.debug(
                    f"Found approval token for action {action_name} in stage "
                    f"{stage_name} of pipeline {pipeline_name}."
                )

                return token
            else:
                logger.debug(
                    f"Action {action_name} in stage {stage_name} of pipeline {pipeline_name} "
                    f"is not awaiting approval or no token is available."
                )

    logger.debug(
        f"No approval token found for action {action_name} in stage "
        f"{stage_name} of pipeline {pipeline_name}."
    )

    return None
