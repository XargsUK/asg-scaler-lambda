import json
from library.codepipeline_event import report_job_success, report_job_failure
from library.asg_helper import update_asg

def lambda_handler(event):
    job_id = event['CodePipeline.job']['id'] if 'CodePipeline.job' in event else None
    
    user_parameters_str = event.get('CodePipeline.job', {}).get('data', {}).get('actionConfiguration', {}).get('configuration', {}).get('UserParameters', '{}')
    try:
        user_parameters = json.loads(user_parameters_str)
    except json.JSONDecodeError:
        report_job_failure(job_id, 'Invalid UserParameters format.')
        return {'statusCode': 400, 'body': json.dumps('Invalid UserParameters format.')}

    params = (
        user_parameters.get('asgName'), 
        user_parameters.get('minCapacity'), 
        user_parameters.get('desiredCapacity'), 
        user_parameters.get('maxCapacity')
    )

    if not all(params) or any(x is None for x in params):
        report_job_failure(job_id, 'Missing required parameters.')
        return {'statusCode': 400, 'body': json.dumps('Missing required parameters.')}

    try:
        message = update_asg(*params)
        report_job_success(job_id)
        return {'statusCode': 200, 'body': json.dumps(message)}
    except ValueError as ve:
        report_job_failure(job_id, str(ve))
        return {'statusCode': 400, 'body': json.dumps(f"Validation Error: {str(ve)}")}
    except Exception as e:
        report_job_failure(job_id, str(e))
        return {'statusCode': 500, 'body': json.dumps(f"Error: {str(e)}")}
