import json
import boto3

def lambda_handler(event):
    """
    AWS Lambda function to update the min, desired, and max capacities of an ASG.

    :param event: The event object that triggered the Lambda. Expected to have 'asgName', 'minCapacity', 'desiredCapacity', and 'maxCapacity'.
    :return: A dictionary with the result of the operation.
    """
    asg_name = event.get('asgName')
    min_capacity = event.get('minCapacity')
    desired_capacity = event.get('desiredCapacity')
    max_capacity = event.get('maxCapacity')

    # Input validation
    if not asg_name or any(x is None for x in [min_capacity, desired_capacity, max_capacity]):
        return {
            'statusCode': 400,
            'body': json.dumps('Missing required parameters: asgName, minCapacity, desiredCapacity, and/or maxCapacity')
        }

    # Capacity validation
    if min_capacity > desired_capacity:
        return {
            'statusCode': 400,
            'body': json.dumps('Incompatible settings: minCapacity cannot be higher than desiredCapacity.')
        }
    
    if desired_capacity > max_capacity:
        return {
            'statusCode': 400,
            'body': json.dumps('Incompatible settings: desiredCapacity cannot be higher than maxCapacity.')
        }

    if min_capacity > max_capacity:
        return {
            'statusCode': 400,
            'body': json.dumps('Incompatible settings: minCapacity cannot be higher than maxCapacity.')
        }

    client = boto3.client('autoscaling')

    try:
        # Update the ASG settings
        client.update_auto_scaling_group(
            AutoScalingGroupName=asg_name,
            MinSize=min_capacity,
            MaxSize=max_capacity,
            DesiredCapacity=desired_capacity
        )

        return {
            'statusCode': 200,
            'body': json.dumps(f"Successfully updated ASG '{asg_name}' settings: Min={min_capacity}, Desired={desired_capacity}, Max={max_capacity}.")
        }
    except client.exceptions.ClientError as e:
        error_message = e.response['Error']['Message']
        print(f"AWS API Error: {error_message}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error updating ASG settings: {error_message}")
        }
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps("Unexpected error occurred.")
        }
