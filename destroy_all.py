import boto3
from botocore.exceptions import ClientError

REGION = "us-east-1"

def delete_cloudformation():
    client = boto3.client('cloudformation', region_name=REGION)
    stacks = client.list_stacks(StackStatusFilter=[
        'CREATE_COMPLETE', 'ROLLBACK_COMPLETE', 'UPDATE_COMPLETE', 'UPDATE_ROLLBACK_COMPLETE'
    ])['StackSummaries']
    for stack in stacks:
        stack_name = stack['StackName']
        print(f"Deleting CloudFormation stack: {stack_name}")
        client.delete_stack(StackName=stack_name)

def delete_eks():
    client = boto3.client('eks', region_name=REGION)
    for cluster in client.list_clusters()['clusters']:
        print(f"Deleting EKS cluster: {cluster}")
        # Delete node groups first
        ngs = client.list_nodegroups(clusterName=cluster)['nodegroups']
        for ng in ngs:
            print(f" - Deleting node group: {ng}")
            client.delete_nodegroup(clusterName=cluster, nodegroupName=ng)
        client.delete_cluster(name=cluster)

def delete_dynamodb():
    client = boto3.client('dynamodb', region_name=REGION)
    for table in client.list_tables()['TableNames']:
        print(f"Deleting DynamoDB table: {table}")
        client.delete_table(TableName=table)

def delete_secrets_manager():
    client = boto3.client('secretsmanager', region_name=REGION)
    for secret in client.list_secrets()['SecretList']:
        print(f"Deleting secret: {secret['Name']}")
        client.delete_secret(SecretId=secret['ARN'], ForceDeleteWithoutRecovery=True)

def delete_s3():
    s3 = boto3.resource('s3', region_name=REGION)
    for bucket in s3.buckets.all():
        print(f"Deleting bucket: {bucket.name}")
        bucket.objects.all().delete()
        bucket.object_versions.all().delete()
        bucket.delete()

def delete_ec2():
    ec2 = boto3.resource('ec2', region_name=REGION)
    client = boto3.client('ec2', region_name=REGION)

    for instance in ec2.instances.all():
        print(f"Terminating EC2 instance: {instance.id}")
        instance.terminate()

    for lb in client.describe_load_balancers()['LoadBalancers']:
        print(f"Deleting Load Balancer: {lb['LoadBalancerArn']}")
        client.delete_load_balancer(LoadBalancerArn=lb['LoadBalancerArn'])

    for tg in client.describe_target_groups()['TargetGroups']:
        print(f"Deleting Target Group: {tg['TargetGroupArn']}")
        client.delete_target_group(TargetGroupArn=tg['TargetGroupArn'])

    for sg in client.describe_security_groups()['SecurityGroups']:
        if sg['GroupName'] != 'default':
            try:
                print(f"Deleting Security Group: {sg['GroupId']}")
                client.delete_security_group(GroupId=sg['GroupId'])
            except ClientError as e:
                print(f"Cannot delete SG {sg['GroupId']}: {e}")

    for vol in ec2.volumes.all():
        if vol.state == 'available':
            print(f"Deleting Volume: {vol.id}")
            vol.delete()

    for eip in client.describe_addresses()['Addresses']:
        print(f"Releasing Elastic IP: {eip['AllocationId']}")
        client.release_address(AllocationId=eip['AllocationId'])

    for kp in client.describe_key_pairs()['KeyPairs']:
        print(f"Deleting Key Pair: {kp['KeyName']}")
        client.delete_key_pair(KeyName=kp['KeyName'])

def delete_rds():
    client = boto3.client('rds', region_name=REGION)
    for db in client.describe_db_instances()['DBInstances']:
        db_id = db['DBInstanceIdentifier']
        print(f"Deleting RDS instance: {db_id}")
        client.delete_db_instance(DBInstanceIdentifier=db_id,
                                  SkipFinalSnapshot=True,
                                  DeleteAutomatedBackups=True)

def delete_lambda():
    client = boto3.client('lambda', region_name=REGION)
    for fn in client.list_functions()['Functions']:
        print(f"Deleting Lambda function: {fn['FunctionName']}")
        client.delete_function(FunctionName=fn['FunctionName'])

def delete_sqs():
    client = boto3.client('sqs', region_name=REGION)
    for queue_url in client.list_queues().get('QueueUrls', []):
        print(f"Deleting SQS queue: {queue_url}")
        client.delete_queue(QueueUrl=queue_url)

def delete_sns():
    client = boto3.client('sns', region_name=REGION)
    for topic in client.list_topics()['Topics']:
        print(f"Deleting SNS topic: {topic['TopicArn']}")
        client.delete_topic(TopicArn=topic['TopicArn'])

def main():
    print(f"Starting full cleanup in {REGION} (excluding IAM)...")
    delete_cloudformation()
    delete_eks()
    delete_dynamodb()
    delete_secrets_manager()
    delete_s3()
    delete_ec2()
    delete_rds()
    delete_lambda()
    delete_sqs()
    delete_sns()
    print("Full cleanup completed.")

if __name__ == "__main__":
    main()
