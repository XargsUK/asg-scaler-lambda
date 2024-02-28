import pytest
from unittest.mock import patch, ANY
import boto3
from moto import mock_aws
from asg_scaler import lambda_handler
import json

import os
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

@pytest.fixture(scope='function')
def aws_resources():
    with mock_aws():
        client = boto3.client('autoscaling', region_name='us-east-1')
        launch_configuration_name = 'test-launch-config'
        client.create_launch_configuration(
            LaunchConfigurationName=launch_configuration_name,
            ImageId='ami-12345678',
            InstanceType='t2.micro'
        )

        yield client

def create_test_asg(client, asg_name, min_size, max_size, desired_capacity):
    client.create_auto_scaling_group(
        AutoScalingGroupName=asg_name,
        LaunchConfigurationName='test-launch-config',
        MinSize=min_size,
        MaxSize=max_size,
        DesiredCapacity=desired_capacity,
        AvailabilityZones=['us-east-1a']
    )

def make_user_parameters(asg_name, min_capacity, desired_capacity, max_capacity):
    """Helper function to create a UserParameters JSON string."""
    params = {
        "asgName": asg_name,
        "minCapacity": min_capacity,
        "desiredCapacity": desired_capacity,
        "maxCapacity": max_capacity
    }
    return json.dumps(params)

@pytest.fixture(scope='function')
def mock_put_job_failure_result():
    with patch('library.codepipeline_event.boto3.client') as mock:
        instance = mock.return_value
        instance.put_job_failure_result.return_value = {}
        yield instance

@pytest.fixture(scope='function')
def mock_put_job_success_result():
    with patch('library.codepipeline_event.boto3.client') as mock:
        instance = mock.return_value
        instance.put_job_success_result.return_value = {}
        yield instance

def test_lambda_handler_success(aws_resources, mock_put_job_success_result):
    asg_name = 'test-asg-success'
    create_test_asg(aws_resources, asg_name, 1, 3, 2)
    
    user_parameters = make_user_parameters(asg_name, 2, 3, 4)
    event = {
        'CodePipeline.job': {
            'id': 'mock_job_id',
            'data': {
                'actionConfiguration': {
                    'configuration': {
                        'UserParameters': user_parameters
                    }
                }
            }
        }
    }
    
    response = lambda_handler(event)
    
    assert response['statusCode'] == 200
    assert 'Successfully updated ASG' in response['body']
    mock_put_job_success_result.put_job_success_result.assert_called_once_with(jobId='mock_job_id')


def test_lambda_handler_failure_missing_parameters(aws_resources, mock_put_job_failure_result):
    user_parameters = json.dumps({"asgName": ""})
    event = {
        'CodePipeline.job': {
            'id': 'mock_job_id',
            'data': {
                'actionConfiguration': {
                    'configuration': {
                        'UserParameters': user_parameters
                    }
                }
            }
        }
    }
    
    response = lambda_handler(event)
    
    assert response['statusCode'] == 400
    assert 'Missing required parameters' in response['body']
    mock_put_job_failure_result.put_job_failure_result.assert_called_once_with(jobId='mock_job_id', failureDetails=ANY)


def test_lambda_handler_failure_min_greater_than_desired(aws_resources, mock_put_job_failure_result):
    asg_name = 'test-failure-min-greater'
    create_test_asg(aws_resources, asg_name, 1, 3, 2)
    
    user_parameters = make_user_parameters(asg_name, 4, 3, 5)  # Min capacity is greater than desired
    event = {
        'CodePipeline.job': {
            'id': 'mock_job_id',
            'data': {
                'actionConfiguration': {
                    'configuration': {
                        'UserParameters': user_parameters
                    }
                }
            }
        }
    }
    
    response = lambda_handler(event)
    
    assert response['statusCode'] == 400
    assert 'Validation Error' in response['body']
    mock_put_job_failure_result.put_job_failure_result.assert_called_once_with(jobId='mock_job_id', failureDetails=ANY)


def test_lambda_handler_failure_desired_greater_than_max(aws_resources, mock_put_job_failure_result):
    asg_name = 'test-failure-desired-greater'
    create_test_asg(aws_resources, asg_name, 1, 3, 2)
    
    user_parameters = make_user_parameters(asg_name, 2, 5, 4)  # Desired capacity is greater than max
    event = {
        'CodePipeline.job': {
            'id': 'mock_job_id',
            'data': {
                'actionConfiguration': {
                    'configuration': {
                        'UserParameters': user_parameters
                    }
                }
            }
        }
    }
    
    response = lambda_handler(event)
    
    assert response['statusCode'] == 400
    assert 'Validation Error' in response['body']
    mock_put_job_failure_result.put_job_failure_result.assert_called_once_with(jobId='mock_job_id', failureDetails=ANY)


def test_lambda_handler_failure_min_greater_than_max(aws_resources, mock_put_job_failure_result):
    asg_name = 'test-failure-min-greater-max'
    create_test_asg(aws_resources, asg_name, 1, 3, 2)
    
    user_parameters = make_user_parameters(asg_name, 5, 4, 3)  # Min capacity is greater than max
    event = {
        'CodePipeline.job': {
            'id': 'mock_job_id',
            'data': {
                'actionConfiguration': {
                    'configuration': {
                        'UserParameters': user_parameters
                    }
                }
            }
        }
    }
    response = lambda_handler(event)
    
    assert response['statusCode'] == 400
    assert 'Validation Error' in response['body']
    mock_put_job_failure_result.put_job_failure_result.assert_called_once_with(jobId='mock_job_id', failureDetails=ANY)
