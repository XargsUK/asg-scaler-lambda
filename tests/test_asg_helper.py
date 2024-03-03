from asg_scaler_lambda.asg_helper import validate_capacities, update_asg
from unittest.mock import patch
import pytest

###########################################
# validate_capacities unit tests
###########################################


def test_validate_capacities_positive():
    # Test case with positive capacities
    min_capacity = 1
    desired_capacity = 2
    max_capacity = 3
    success, error_message = validate_capacities(min_capacity, desired_capacity, max_capacity)
    assert success == True
    assert error_message == ""


def test_validate_capacities_negative():
    # Test case with negative capacities
    min_capacity = -1
    desired_capacity = -2
    max_capacity = -3
    success, error_message = validate_capacities(min_capacity, desired_capacity, max_capacity)
    assert success == False
    assert error_message == "Capacity settings cannot be negative."


def test_validate_capacities_incompatible():
    # Test case with incompatible capacities
    min_capacity = 5
    desired_capacity = 4
    max_capacity = 3
    success, error_message = validate_capacities(min_capacity, desired_capacity, max_capacity)
    assert success == False
    assert error_message == "Incompatible settings: Check your capacity settings."


def test_validate_capacities_equal():
    # Test case with equal capacities
    min_capacity = 3
    desired_capacity = 3
    max_capacity = 3
    success, error_message = validate_capacities(min_capacity, desired_capacity, max_capacity)
    assert success == True
    assert error_message == ""

###########################################
# update_asg unit tests
###########################################


@patch('asg_scaler_lambda.asg_helper.boto3.client')
def test_update_asg_positive(mock_boto3_client):
    mock_boto3_client.return_value.update_auto_scaling_group.return_value = {}

    # Test case with positive capacities
    asg_name = "my-asg"
    min_capacity = "1"
    desired_capacity = "2"
    max_capacity = "3"
    success_message = update_asg(asg_name, min_capacity, desired_capacity, max_capacity)
    assert success_message == "Successfully updated ASG 'my-asg' settings: Min=1, Desired=2, Max=3."


@patch('asg_scaler_lambda.asg_helper.boto3.client')
def test_update_asg_negative(mock_boto3_client):
    mock_boto3_client.return_value.update_auto_scaling_group.return_value = {}

    # Test case with negative capacities
    asg_name = "my-asg"
    min_capacity = "-1"
    desired_capacity = "-2"
    max_capacity = "-3"
    with pytest.raises(ValueError) as excinfo:
        update_asg(asg_name, min_capacity, desired_capacity, max_capacity)
    assert str(excinfo.value) == "Capacity settings cannot be negative."


@patch('asg_scaler_lambda.asg_helper.boto3.client')
def test_update_asg_incompatible(mock_boto3_client):
    mock_boto3_client.return_value.update_auto_scaling_group.return_value = {}

    # Test case with incompatible capacities
    asg_name = "my-asg"
    min_capacity = "5"
    desired_capacity = "4"
    max_capacity = "3"
    with pytest.raises(ValueError) as excinfo:
        update_asg(asg_name, min_capacity, desired_capacity, max_capacity)
    assert str(excinfo.value) == "Incompatible settings: Check your capacity settings."


@patch('asg_scaler_lambda.asg_helper.boto3.client')
def test_update_asg_equal(mock_boto3_client):
    # Mock the response of update_auto_scaling_group
    mock_boto3_client.return_value.update_auto_scaling_group.return_value = {}

    # Test case with equal capacities
    asg_name = "my-asg"
    min_capacity = "3"
    desired_capacity = "3"
    max_capacity = "3"
    success_message = update_asg(asg_name, min_capacity, desired_capacity, max_capacity)
    assert success_message == "Successfully updated ASG 'my-asg' settings: Min=3, Desired=3, Max=3."
