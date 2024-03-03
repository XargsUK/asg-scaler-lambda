import json
import logging
from asg_scaler_lambda.codepipeline_event import (
    report_job_success, report_job_failure, 
    get_approval_token, approve_action
)
from asg_scaler_lambda.asg_helper import update_asg

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def lambda_handler(event, context):
    logger.info(f"Received event: {event}")
    if 'CodePipeline.job' in event:
        return handle_codepipeline_event(event)
    elif event.get('source') == 'aws.codedeploy' and event.get('detail', {}).get('state') == 'SUCCESS':
        return handle_eventbridge_event(event)
    else:
        logger.warning('Event source not recognised.')
        return {'statusCode': 400, 'body': 'Event source not recognised.'}


def handle_codepipeline_event(event):
    job_id = event['CodePipeline.job']['id'] if 'CodePipeline.job' in event else None

    code_pipeline_job = event.get('CodePipeline.job', {})
    job_data = code_pipeline_job.get('data', {})
    action_configuration = job_data.get('actionConfiguration', {})
    configuration = action_configuration.get('configuration', {})
    user_parameters_str = configuration.get('UserParameters', '{}')


    try:
        user_parameters = json.loads(user_parameters_str)
    except json.JSONDecodeError:
        report_job_failure(job_id, 'Invalid UserParameters format.')
        logger.error(f"Invalid UserParameters format for job {job_id}.")
        return {'statusCode': 400, 'body': json.dumps('Invalid UserParameters format.')}

    params = (
        user_parameters.get('asgName'),
        user_parameters.get('minCapacity'),
        user_parameters.get('desiredCapacity'),
        user_parameters.get('maxCapacity')
    )

    if not all(params) or any(x is None for x in params):
        report_job_failure(job_id, 'Missing required parameters.')
        logger.error(f"Missing required parameters for job {job_id}.")
        return {'statusCode': 400, 'body': json.dumps('Missing required parameters.')}

    try:
        message = update_asg(*params)
        report_job_success(job_id)
        logger.info(f"Successfully processed CodePipeline job {job_id}: {message}")
        return {'statusCode': 200, 'body': json.dumps(message)}
    except ValueError as ve:
        report_job_failure(job_id, str(ve))
        logger.error(f"Validation Error for job {job_id}: {str(ve)}")
        return {'statusCode': 400, 'body': json.dumps(f"Validation Error: {str(ve)}")}
    except Exception as e:
        report_job_failure(job_id, str(e))
        logger.error(f"Error processing CodePipeline job {job_id}: {str(e)}")
        return {'statusCode': 500, 'body': json.dumps(f"Error: {str(e)}")}


def handle_eventbridge_event(event):
    logger.info(f"Processing EventBridge event: {event}")
    pipeline_name = event.get('pipelineName')
    stage_name = event.get('stageName')
    action_name = event.get('actionName')

    token = get_approval_token(pipeline_name, stage_name, action_name)
    if token:
        result = approve_action(pipeline_name, stage_name, action_name, token)
        logger.info(f"EventBridge event processed for pipeline {pipeline_name}. Result: {result}")
        return result
    else:
        logger.warning(
            f"No approval token available or action not in a state that can be "
            f"approved for pipeline {pipeline_name}."
        )

        return {'statusCode': 400, 'body': 'Approval token not found.'}
