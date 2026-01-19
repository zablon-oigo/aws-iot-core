### Ingesting Streaming Data from AWS IoT Core into DynamoDB

This project demonstrates how to ingest streaming IoT data into Amazon DynamoDB using AWS IoT Core, Lambda, and a Python-based IoT device simulator.

A Python script simulates an IoT device by publishing MQTT messages to AWS IoT Core. An IoT Core Rule forwards these messages to a Lambda function for lightweight transformation before persisting them into DynamoDB.

#### Architecture Diagram


### Setup Guide 
Create an IoT Policy
```bash
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iot:Connect",
        "iot:Publish",
        "iot:Subscribe",
        "iot:Receive"
      ],
      "Resource": "*"
    }
  ]
}

```
Create it via CLI:
```bash
aws iot create-policy \
  --policy-name distancePolicy \
  --policy-document file://distancePolicy.json
```
Download the Amazon Root CA
```bash
curl https://www.amazontrust.com/repository/AmazonRootCA1.pem  > root-CA.crt
```

Create an IoT Thing
```bash
aws iot create-thing --thing-name distance

```
Create Device Certificates
```bash
aws iot create-keys-and-certificate \
  --set-as-active \
  --certificate-pem-outfile certificate.pem.crt \
  --private-key-outfile private.pem.key

```
Save the certificate ARN from the output.

Attach Policy to Certificate
```bash
aws iot attach-policy \
  --policy-name distancePolicy \
  --target YOUR_CERT_ARN

```
Get Your AWS IoT Endpoint
```bash
aws iot describe-endpoint --endpoint-type iot:Data-ATS
```

DynamoDB Setup
Create a DynamoDB table:
- Table name: data_v1
- Partition key: timestamp (String)

```bash
aws dynamodb create-table \
  --table-name data_v1 \
  --attribute-definitions AttributeName=timestamp,AttributeType=S \
  --key-schema AttributeName=timestamp,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

```

Lambda Function
The Lambda function receives IoT messages and writes them to DynamoDB.

```bash
import boto3

dynamodb = boto3.client('dynamodb')

def lambda_handler(event, context):
    dynamodb.put_item(
        TableName='data_v1',
        Item={
            'timestamp': {'S': event['timestamp']},
            'distance_cm': {'N': str(event['distance_cm'])},
            'status': {'S': event['status']}
        }
    )
    return {
        "statusCode": 200,
        "body": "Item inserted"
    }
```
IAM Permissions for Lambda
Attach this policy to the Lambda execution role:
```bash
{
  "Effect": "Allow",
  "Action": "dynamodb:PutItem",
  "Resource": "arn:aws:dynamodb:REGION:ACCOUNT_ID:table/data_v1"
}

```

AWS IoT Rule
Create an IoT Rule:
```sql
SELECT * FROM 'iot/simulator/distance'
```
Running the Simulator
Start publishing IoT data:
```bash
python main.py
```
Example payload sent:
```bash
{
  "timestamp": "2026-01-18T09:35:00+00:00",
  "distance_cm": 45,
  "status": "GREEN"
}
```
