import boto3 

def lambda_handler(event, context):
    client=boto3.client('dynamodb')

    response = client.put_item(
        TableName='data_v1',
        Item={
            'timestamp': {'S': event['timestamp']},
            'distance_cm': {'N': str(event['distance_cm'])},
            'status': {'S': event['status']}
        }
    )

    return 0