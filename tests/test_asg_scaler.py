import json
from unittest.mock import patch
from asg_scaler_lambda.asg_scaler import lambda_handler


@patch('asg_scaler_lambda.asg_scaler.update_asg')
@patch('asg_scaler_lambda.asg_scaler.report_job_success')
def test_lambda_handler_codepipeline_success(mock_report_job_success, mock_update_asg):
    mock_update_asg.return_value = "ASG updated successfully"

    event = {
        "CodePipeline.job": {
            "id": "1234",
            "data": {
                "actionConfiguration": {
                    "configuration": {
                        "UserParameters": json.dumps({
                            "asgName": "test-asg",
                            "minCapacity": "1",
                            "desiredCapacity": "2",
                            "maxCapacity": "3"
                        })
                    }
                }
            }
        }
    }

    response = lambda_handler(event, {})
    assert response['statusCode'] == 200
    assert json.loads(response['body']) == "ASG updated successfully"
    mock_update_asg.assert_called_once_with("test-asg", "1", "2", "3")
    mock_report_job_success.assert_called_once_with("1234")

##################################################
# CodePipeline event with invalid user parameters
##################################################


@patch('asg_scaler_lambda.asg_scaler.report_job_failure')
def test_lambda_handler_codepipeline_invalid_user_parameters(mock_report_job_failure):
    event = {
        "CodePipeline.job": {
            "id": "1234",
            "data": {
                "actionConfiguration": {
                    "configuration": {
                        "UserParameters": "invalid_json"
                    }
                }
            }
        }
    }

    response = lambda_handler(event, {})
    assert response['statusCode'] == 400
    assert json.loads(response['body']) == "Invalid UserParameters format."
    mock_report_job_failure.assert_called_once_with("1234", "Invalid UserParameters format.")

##################################################
# CodePipeline event with missing user parameters
##################################################


@patch('asg_scaler_lambda.asg_scaler.report_job_failure')
def test_lambda_handler_codepipeline_missing_required_parameters(mock_report_job_failure):
    event = {
        "CodePipeline.job": {
            "id": "1234",
            "data": {
                "actionConfiguration": {
                    "configuration": {
                        "UserParameters": json.dumps({})
                    }
                }
            }
        }
    }

    response = lambda_handler(event, {})
    assert response['statusCode'] == 400
    assert json.loads(response['body']) == "Missing required parameters."
    mock_report_job_failure.assert_called_once_with("1234", "Missing required parameters.")

##################################################
# CodePipeline event with update_asg ValueError
##################################################


@patch('asg_scaler_lambda.asg_scaler.report_job_failure')
@patch('asg_scaler_lambda.asg_scaler.update_asg', side_effect=ValueError("Validation Error"))
def test_lambda_handler_codepipeline_update_failure(mock_update_asg, mock_report_job_failure):
    event = {
        "CodePipeline.job": {
            "id": "1234",
            "data": {
                "actionConfiguration": {
                    "configuration": {
                        "UserParameters": json.dumps({
                            "asgName": "test-asg",
                            "minCapacity": "1",
                            "desiredCapacity": "2",
                            "maxCapacity": "3"
                        })
                    }
                }
            }
        }
    }

    response = lambda_handler(event, {})
    assert response['statusCode'] == 400
    assert json.loads(response['body']) == "Validation Error: Validation Error"
    mock_report_job_failure.assert_called_once_with("1234", "Validation Error")

##################################################
# EventBridge event with successful approval
##################################################


@patch('asg_scaler_lambda.asg_scaler.approve_action')
@patch('asg_scaler_lambda.asg_scaler.get_approval_token')
def test_lambda_handler_eventbridge_success(mock_get_approval_token, mock_approve_action):
    event = {
        "source": "aws.codedeploy",
        "detail": {
            "state": "SUCCESS"
        },
        "pipelineName": "test-pipeline",
        "stageName": "test-stage",
        "actionName": "test-action"
    }

    # Mocking get_approval_token to return a non-None value
    mock_get_approval_token.return_value = 'token123'

    # Mocking approve_action to return a response
    mock_approve_action.return_value = {'statusCode': 200, 'body': 'Approval submitted successfully.'}

    response = lambda_handler(event, {})
    assert response['statusCode'] == 200
    assert response['body'] == "Approval submitted successfully."
    mock_get_approval_token.assert_called_once_with("test-pipeline", "test-stage", "test-action")
    mock_approve_action.assert_called_once_with("test-pipeline", "test-stage", "test-action", "token123")


@patch('asg_scaler_lambda.asg_scaler.get_approval_token', return_value=None)
def test_lambda_handler_eventbridge_no_token(mock_get_approval_token):
    event = {
        "source": "aws.codedeploy",
        "detail": {
            "state": "SUCCESS"
        },
        "pipelineName": "test-pipeline",
        "stageName": "test-stage",
        "actionName": "test-action"
    }

    response = lambda_handler(event, {})
    assert response['statusCode'] == 400
    assert response['body'] == "Approval token not found."
    mock_get_approval_token.assert_called_once_with("test-pipeline", "test-stage", "test-action")
