import boto3

def update_asg(asg_name, min_capacity, desired_capacity, max_capacity):
    """
    Update the specified Auto Scaling Group's capacities.
    Converts string input to integers and validates them before updating.

    :param asg_name: The name of the Auto Scaling Group to update
    :param min_capacity: The minimum size of the ASG
    :param desired_capacity: The desired size of the ASG
    :param max_capacity: The maximum size of the ASG
    :return: A success message string
    :raises ValueError: If the validation fails or the update operation fails
    """
    # Convert capacity parameters to integers
    try:
        min_capacity = int(min_capacity)
        desired_capacity = int(desired_capacity)
        max_capacity = int(max_capacity)
    except ValueError:
        raise ValueError("Capacity parameters must be integers.")

    # Validate the converted capacities
    valid, message = validate_capacities(min_capacity, desired_capacity, max_capacity)
    if not valid:
        raise ValueError(message)

    client = boto3.client('autoscaling')
    client.update_auto_scaling_group(
        AutoScalingGroupName=asg_name,
        MinSize=min_capacity,
        MaxSize=max_capacity,
        DesiredCapacity=desired_capacity
    )
    return f"Successfully updated ASG '{asg_name}' settings: Min={min_capacity}, Desired={desired_capacity}, Max={max_capacity}."

def validate_capacities(min_capacity, desired_capacity, max_capacity):
    """
    Validate the ASG capacities to ensure they are logically consistent and non-negative.

    :param min_capacity: The minimum size of the ASG
    :param desired_capacity: The desired size of the ASG
    :param max_capacity: The maximum size of the ASG
    :return: A tuple (bool, str) where the first element indicates success/failure, and the second is the error message (if any)
    """
    # Check for negative values
    if min_capacity < 0 or desired_capacity < 0 or max_capacity < 0:
        return False, "Capacity settings cannot be negative."

    if min_capacity > desired_capacity or desired_capacity > max_capacity or min_capacity > max_capacity:
        return False, "Incompatible settings: Check your capacity settings."

    return True, ""
