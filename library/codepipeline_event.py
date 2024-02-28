import boto3

def report_job_success(job_id):
    """
    Notify AWS CodePipeline of a successful job execution.
    :param job_id: The ID of the CodePipeline job
    """
    client = boto3.client('codepipeline')
    client.put_job_success_result(jobId=job_id)

def report_job_failure(job_id, message):
    """
    Notify AWS CodePipeline of a failed job execution.

    :param job_id: The ID of the CodePipeline job
    :param message: The failure message to report back to CodePipeline
    """
    client = boto3.client('codepipeline')
    client.put_job_failure_result(
        jobId=job_id,
        failureDetails={'message': message, 'type': 'JobFailed'}
    )
