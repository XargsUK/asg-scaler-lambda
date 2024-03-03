from asg_scaler_lambda.codepipeline_event import (
    report_job_success, report_job_failure, approve_action,
    get_approval_token, find_action_in_stage, extract_token_if_available
)
from unittest.mock import patch, MagicMock
import json

############################################
# report_job_success unit tests
############################################


@patch('asg_scaler_lambda.codepipeline_event.get_codepipeline_client')
def test_report_job_success_success(mock_get_client):
    # Create a mock client object
    mock_client = MagicMock()
    # Configure the mock get_codepipeline_client function to return the mock client
    mock_get_client.return_value = mock_client
    # Mock the response of put_job_success_result
    mock_client.put_job_success_result.return_value = {}

    # Test case with successful job execution
    job_id = "12345"
    report_job_success(job_id)

    # Assert that put_job_success_result was called with the correct job ID
    mock_client.put_job_success_result.assert_called_once_with(jobId=job_id)


@patch('asg_scaler_lambda.codepipeline_event.get_codepipeline_client')
def test_report_job_failure_exception(mock_get_client):
    # Create a mock client object
    mock_client = MagicMock()
    # Mock the response of put_job_failure_result to raise an exception
    mock_client.put_job_failure_result.side_effect = Exception("Some error")
    # Configure the mock get_codepipeline_client function to return the mock client
    mock_get_client.return_value = mock_client

    # Test case with exception during job failure reporting
    job_id = "12345"
    message = "Failure message"
    report_job_failure(job_id, message)  # This should not raise an exception, as the function catches it

    # Assert that put_job_failure_result was called with the correct job ID and message
    mock_client.put_job_failure_result.assert_called_once_with(
        jobId=job_id,
        failureDetails={'message': message, 'type': 'JobFailed'}
    )

############################################
# approve_action unit tests
############################################


@patch('asg_scaler_lambda.codepipeline_event.get_codepipeline_client')
def test_approve_action_success(mock_get_client):
    # Setup mock client and response
    mock_client = MagicMock()
    mock_client.put_approval_result.return_value = {
        'ResponseMetadata': {
            'HTTPStatusCode': 200
        }
    }
    mock_get_client.return_value = mock_client

    # Execute the function under test
    pipeline_name = "test-pipeline"
    stage_name = "test-stage"
    action_name = "test-action"
    token = "test-token"
    response = approve_action(pipeline_name, stage_name, action_name, token)

    # Assertions
    assert response['statusCode'] == 200
    assert json.loads(response['body']) == 'Approval submitted successfully.'
    mock_client.put_approval_result.assert_called_once_with(
        pipelineName=pipeline_name,
        stageName=stage_name,
        actionName=action_name,
        result={'summary': 'Deployment successful, automatically approved by Lambda.', 'status': 'Approved'},
        token=token
    )


@patch('asg_scaler_lambda.codepipeline_event.get_codepipeline_client')
def test_approve_action_failure(mock_get_client):
    # Setup mock client to raise an exception
    mock_client = MagicMock()
    mock_client.put_approval_result.side_effect = Exception("AWS service exception")
    mock_get_client.return_value = mock_client

    # Execute the function under test
    pipeline_name = "test-pipeline"
    stage_name = "test-stage"
    action_name = "test-action"
    token = "test-token"
    response = approve_action(pipeline_name, stage_name, action_name, token)

    # Assertions
    assert response['statusCode'] == 500
    assert "Error processing approval" in json.loads(response['body'])
    mock_client.put_approval_result.assert_called_once_with(
        pipelineName=pipeline_name,
        stageName=stage_name,
        actionName=action_name,
        result={'summary': 'Deployment successful, automatically approved by Lambda.', 'status': 'Approved'},
        token=token
    )

############################################
# get_approval_token  unit tests
############################################


@patch('asg_scaler_lambda.codepipeline_event.get_codepipeline_client')
def test_get_approval_token_success(mock_get_client):
    # Setup mock client and response
    mock_client = MagicMock()
    mock_client.get_pipeline_state.return_value = {
        'stageStates': [
            {
                'stageName': 'test-stage',
                'actionStates': [
                    {
                        'actionName': 'test-action',
                        'latestExecution': {
                            'status': 'InProgress',
                            'token': 'test-token'
                        }
                    }
                ]
            }
        ]
    }
    mock_get_client.return_value = mock_client

    # Execute the function under test
    pipeline_name = "test-pipeline"
    stage_name = "test-stage"
    action_name = "test-action"
    token = get_approval_token(pipeline_name, stage_name, action_name)

    # Assertions
    assert token == 'test-token'
    mock_client.get_pipeline_state.assert_called_once_with(name=pipeline_name)


@patch('asg_scaler_lambda.codepipeline_event.get_codepipeline_client')
def test_get_approval_token_no_token_available(mock_get_client):
    # Setup mock client to return a state without an available token
    mock_client = MagicMock()
    mock_client.get_pipeline_state.return_value = {
        'stageStates': [
            {
                'stageName': 'test-stage',
                'actionStates': [
                    {
                        'actionName': 'test-action',
                        'latestExecution': {
                            'status': 'Succeeded',  # Not InProgress, so no token should be available
                        }
                    }
                ]
            }
        ]
    }
    mock_get_client.return_value = mock_client

    # Execute the function under test
    pipeline_name = "test-pipeline"
    stage_name = "test-stage"
    action_name = "test-action"
    token = get_approval_token(pipeline_name, stage_name, action_name)

    # Assertions
    assert token is None
    mock_client.get_pipeline_state.assert_called_once_with(name=pipeline_name)


@patch('asg_scaler_lambda.codepipeline_event.get_codepipeline_client')
def test_get_approval_token_api_exception(mock_get_client):
    # Setup mock client to raise an exception
    mock_client = MagicMock()
    mock_client.get_pipeline_state.side_effect = Exception("AWS service exception")
    mock_get_client.return_value = mock_client

    # Execute the function under test
    pipeline_name = "test-pipeline"
    stage_name = "test-stage"
    action_name = "test-action"
    token = get_approval_token(pipeline_name, stage_name, action_name)

    # Assertions
    assert token is None
    mock_client.get_pipeline_state.assert_called_once_with(name=pipeline_name)

############################################
# find_action_in_stage unit tests
############################################


def test_find_action_in_stage_found():
    stage = {
        'actionStates': [
            {'actionName': 'deploy', 'latestExecution': {'status': 'Succeeded'}},
            {'actionName': 'test-action', 'latestExecution': {'status': 'InProgress'}},
        ]
    }
    action_name = 'test-action'
    found_action = find_action_in_stage(stage, action_name)
    assert found_action is not None
    assert found_action['actionName'] == action_name


def test_find_action_in_stage_not_found():
    stage = {
        'actionStates': [
            {'actionName': 'deploy', 'latestExecution': {'status': 'Succeeded'}},
        ]
    }
    action_name = 'missing-action'
    found_action = find_action_in_stage(stage, action_name)
    assert found_action is None

############################################
# extract_token_if_available unit tests
############################################


def test_extract_token_if_available_with_token():
    action = {
        'actionName': 'test-action',
        'latestExecution': {
            'status': 'InProgress',
            'token': 'test-token'
        }
    }
    token = extract_token_if_available(action)
    assert token == 'test-token'


def test_extract_token_if_available_without_token():
    action = {
        'actionName': 'test-action',
        'latestExecution': {
            'status': 'InProgress',
            # No token present
        }
    }
    token = extract_token_if_available(action)
    assert token is None


def test_extract_token_if_available_wrong_status():
    action = {
        'actionName': 'test-action',
        'latestExecution': {
            'status': 'Succeeded',  # Not InProgress
            'token': 'test-token'
        }
    }
    token = extract_token_if_available(action)
    assert token is None
