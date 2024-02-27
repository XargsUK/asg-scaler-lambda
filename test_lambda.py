import pytest
from moto import mock_aws
import boto3
from asg_scaler import lambda_handler
import os

os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

@pytest.fixture
def aws_client():
    with mock_aws():
        client = boto3.client('autoscaling', region_name='us-east-1')
        yield client

def create_test_asg(client, asg_name, min_size, max_size, desired_capacity):
    launch_configuration_name = 'test-launch-config'
    client.create_launch_configuration(
        LaunchConfigurationName=launch_configuration_name,
        ImageId='ami-12345678',
        InstanceType='t2.micro'
    )
    client.create_auto_scaling_group(
        AutoScalingGroupName=asg_name,
        LaunchConfigurationName=launch_configuration_name,
        MinSize=min_size,
        MaxSize=max_size,
        DesiredCapacity=desired_capacity,
        AvailabilityZones=['us-east-1a']
    )

def test_lambda_handler_success(aws_client):
    asg_name = 'test-asg-success'
    create_test_asg(aws_client, asg_name, 1, 3, 2)
    
    event = {
        'asgName': asg_name,
        'minCapacity': 2,
        'desiredCapacity': 3,
        'maxCapacity': 4
    }
    
    response = lambda_handler(event)
    
    assert response['statusCode'] == 200
    assert 'Successfully updated ASG' in response['body']

def test_lambda_handler_failure_missing_parameters(aws_client):
    event = {'asgName': ''}
    
    response = lambda_handler(event)
    
    assert response['statusCode'] == 400
    assert 'Missing required parameters' in response['body']

def test_lambda_handler_success_equal_capacities(aws_client):
    asg_name = 'test-asg-equal-capacities'
    create_test_asg(aws_client, asg_name, 1, 2, 2)
    
    event = {
        'asgName': asg_name,
        'minCapacity': 3,
        'desiredCapacity': 3,
        'maxCapacity': 3
    }
    
    response = lambda_handler(event)
    
    assert response['statusCode'] == 200
    assert 'Successfully updated ASG' in response['body']