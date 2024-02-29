import boto3
import json
import logging

# Configure the logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

client = boto3.client('codepipeline')

def report_job_success(job_id):
    """
    Notify AWS CodePipeline of a successful job execution.
    :param job_id: The ID of the CodePipeline job
    """
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
    try:
        client.put_job_failure_result(
            jobId=job_id,
            failureDetails={'message': message, 'type': 'JobFailed'}
        )
        logger.debug(f"Job {job_id} reported as failure. Message: {message}")
    except Exception as e:
        logger.debug(f"Error reporting job failure for {job_id}: {str(e)}")

def approve_action(pipeline_name, stage_name, action_name, token):
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
        logger.debug(f"Approval submitted successfully for action {action_name} in stage {stage_name} of pipeline {pipeline_name}: {response}")
        return {'statusCode': 200, 'body': json.dumps('Approval submitted successfully.')}
    except Exception as e:
        logger.debug(f"Error submitting approval for action {action_name} in pipeline {pipeline_name}: {str(e)}")
        return {'statusCode': 500, 'body': json.dumps(f"Error processing approval: {str(e)}")}
    
def get_approval_token(pipeline_name, stage_name, action_name):
    try:
        pipeline_state = client.get_pipeline_state(name=pipeline_name)
        for stage in pipeline_state['stageStates']:
            if stage['stageName'] == stage_name:
                for action in stage['actionStates']:
                    if action['actionName'] == action_name:
                        latest_execution = action.get('latestExecution', {})
                        if latest_execution.get('status') == 'InProgress' and 'token' in latest_execution:
                            logger.debug(f"Found approval token for action {action_name} in stage {stage_name} of pipeline {pipeline_name}.")
                            return latest_execution['token']
                        else:
                            logger.debug(f"Action {action_name} in stage {stage_name} of pipeline {pipeline_name} is not awaiting approval or no token is available.")
                            return None
    except Exception as e:
        logger.debug(f"Error getting pipeline state for {pipeline_name}: {str(e)}")
        return None

    logger.debug(f"No approval token found for action {action_name} in stage {stage_name} of pipeline {pipeline_name}.")
    return None
