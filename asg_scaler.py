import json
from library.codepipeline_event import report_job_success, report_job_failure
from library.codedeploy_helper import monitor_deployments
from library.asg_helper import update_asg
from datetime import datetime, timezone

def lambda_handler(event, context):
    job_id = event['CodePipeline.job']['id'] if 'CodePipeline.job' in event else None
    invocation_time = datetime.now(timezone.utc)

    try:
        user_parameters_str = event.get('CodePipeline.job', {}).get('data', {}).get('actionConfiguration', {}).get('configuration', {}).get('UserParameters', '{}')
        user_parameters = json.loads(user_parameters_str)
    except json.JSONDecodeError:
        report_job_failure(job_id, 'Invalid UserParameters format.')
        return {'statusCode': 400, 'body': json.dumps('Invalid UserParameters format.')}

    asg_name = user_parameters.get('asgName')
    min_capacity = user_parameters.get('minCapacity')
    desired_capacity = user_parameters.get('desiredCapacity')
    max_capacity = user_parameters.get('maxCapacity')
    application_name = user_parameters.get('applicationName')
    deployment_group_name = user_parameters.get('deploymentGroupName')

    if not all([asg_name, min_capacity, desired_capacity, max_capacity, application_name, deployment_group_name]):
        report_job_failure(job_id, 'Missing required parameters.')
        return {'statusCode': 400, 'body': json.dumps('Missing required parameters.')}

    try:
        # Update ASG capacities
        message = update_asg(asg_name, min_capacity, desired_capacity, max_capacity)
        print(message)

        # Monitor deployments
        success, status = monitor_deployments(application_name, deployment_group_name, invocation_time=invocation_time)
        if success:
            print("Deployment monitoring succeeded.")
            report_job_success(job_id)
            return {'statusCode': 200, 'body': json.dumps('ASG scaled and all deployments succeeded.')}
        else:
            print(f"Deployment monitoring failed due to: {status}")
            report_job_failure(job_id, f"Deployment monitoring failed due to: {status}")
            return {'statusCode': 400, 'body': json.dumps(f"Deployment monitoring failed due to: {status}")}

    except Exception as e:
        report_job_failure(job_id, str(e))
        return {'statusCode': 500, 'body': json.dumps(f"Error: {str(e)}")}
