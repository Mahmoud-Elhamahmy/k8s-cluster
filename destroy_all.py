import boto3
from botocore.exceptions import ClientError

REGION = "us-east-1"

def delete_cloudformation():
    client = boto3.client('cloudformation', region_name=REGION)
    try:
        stacks = client.list_stacks(StackStatusFilter=[
            'CREATE_COMPLETE', 'ROLLBACK_COMPLETE', 'UPDATE_COMPLETE', 'UPDATE_ROLLBACK_COMPLETE'
        ])['StackSummaries']
        for stack in stacks:
            stack_name = stack['StackName']
            print(f"Deleting CloudFormation stack: {stack_name}")
            client.delete_stack(StackName=stack_name)
    except ClientError as e:
        print(f"Skipping CloudFormation: {e}")

def delete_eks():
    client = boto3.client('eks', region_name=REGION)
    try:
        clusters = client.list_clusters()['clusters']
        for cluster in clusters:
            print(f"Deleting EKS cluster: {cluster}")
            ngs = client.list_nodegroups(clusterName=cluster)['nodegroups']
            for ng in ngs:
                print(f" - Deleting node group: {ng}")
                client.delete_nodegroup(clusterName=cluster, nodegroupName=ng)
            client.delete_cluster(name=cluster)
    except ClientError as e:
        print(f"Skipping EKS: {e}")

def delete_dynamodb():
    client = boto3.client('dynamodb', region_name=REGION)
    try:
        for table in client.list_tables()['TableNames']:
            print(f"Deleting DynamoDB table: {table}")
            client.delete_table(TableName=table)
    except ClientError as e:
        print(f"Skipping DynamoDB: {e}")

def delete_secrets_manager():
    client = boto3.client('secretsmanager', region_name=REGION)
    try:
        for secret in client.list_secrets()['SecretList']:
            print(f"Deleting secret: {secret['Name']}")
            client.delete_secret(SecretId=secret['ARN'], ForceDeleteWithoutRecovery=True)
    except ClientError as e:
        print(f"Skipping Secrets Manager: {e}")

def delete_s3():
    s3 = boto3.resource('s3', region_name=REGION)
    try:
        for bucket in s3.buckets.all():
            print(f"Deleting bucket: {bucket.name}")
            bucket.objects.all().delete()
            bucket.object_versions.all().delete()
            bucket.delete()
    except ClientError as e:
        print(f"Skipping S3: {e}")

def delete_load_balancers():
    elb = boto3.client('elbv2', region_name=REGION)
    try:
        lbs = elb.describe_load_balancers()['LoadBalancers']
        for lb in lbs:
            lb_arn = lb['LoadBalancerArn']
            print(f"Deleting Load Balancer: {lb_arn}")
            elb.delete_load_balancer(LoadBalancerArn=lb_arn)
    except ClientError as e:
        print(f"Skipping Load Balancers: {e}")

    try:
        tgs = elb.describe_target_groups()['TargetGroups']
        for tg in tgs:
            tg_arn = tg['TargetGroupArn']
            print(f"Deleting Target Group: {tg_arn}")
            elb.delete_target_group(TargetGroupArn=tg_arn)
    except ClientError as e:
        print(f"Skipping Target Groups: {e}")

def delete_ec2():
    ec2 = boto3.resource('ec2', region_name=REGION)
    client = boto3.client('ec2', region_name=REGION)
    try:
        for instance in ec2.instances.all():
            print(f"Terminating EC2 instance: {instance.id}")
            instance.terminate()

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
    except ClientError as e:
        print(f"Skipping EC2: {e}")

def delete_rds():
    client = boto3.client('rds', region_name=REGION)
    try:
        for db in client.describe_db_instances()['DBInstances']:
            db_id = db['DBInstanceIdentifier']
            print(f"Deleting RDS instance: {db_id}")
            client.delete_db_instance(DBInstanceIdentifier=db_id,
                                      SkipFinalSnapshot=True,
                                      DeleteAutomatedBackups=True)
    except ClientError as e:
        print(f"Skipping RDS: {e}")

def delete_lambda():
    client = boto3.client('lambda', region_name=REGION)
    try:
        for fn in client.list_functions()['Functions']:
            print(f"Deleting Lambda function: {fn['FunctionName']}")
            client.delete_function(FunctionName=fn['FunctionName'])
    except ClientError as e:
        print(f"Skipping Lambda: {e}")

def delete_sqs():
    client = boto3.client('sqs', region_name=REGION)
    try:
        for queue_url in client.list_queues().get('QueueUrls', []):
            print(f"Deleting SQS queue: {queue_url}")
            client.delete_queue(QueueUrl=queue_url)
    except ClientError as e:
        print(f"Skipping SQS: {e}")

def delete_sns():
    client = boto3.client('sns', region_name=REGION)
    try:
        for topic in client.list_topics()['Topics']:
            print(f"Deleting SNS topic: {topic['TopicArn']}")
            client.delete_topic(TopicArn=topic['TopicArn'])
    except ClientError as e:
        print(f"Skipping SNS: {e}")

def delete_network_resources():
    client = boto3.client('ec2', region_name=REGION)
    try:
        # Delete NAT Gateways
        for ngw in client.describe_nat_gateways()['NatGateways']:
            ngw_id = ngw['NatGatewayId']
            print(f"Deleting NAT Gateway: {ngw_id}")
            client.delete_nat_gateway(NatGatewayId=ngw_id)

        # Detach and delete Internet Gateways
        for igw in client.describe_internet_gateways()['InternetGateways']:
            igw_id = igw['InternetGatewayId']
            for attachment in igw.get('Attachments', []):
                vpc_id = attachment['VpcId']
                print(f"Detaching IGW {igw_id} from VPC {vpc_id}")
                client.detach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
            print(f"Deleting Internet Gateway: {igw_id}")
            client.delete_internet_gateway(InternetGatewayId=igw_id)

        # Delete Route Tables (except main)
        for rt in client.describe_route_tables()['RouteTables']:
            associations = rt.get('Associations', [])
            if not any(assoc.get('Main') for assoc in associations):
                print(f"Deleting Route Table: {rt['RouteTableId']}")
                client.delete_route_table(RouteTableId=rt['RouteTableId'])

        # Delete Subnets
        for subnet in client.describe_subnets()['Subnets']:
            print(f"Deleting Subnet: {subnet['SubnetId']}")
            client.delete_subnet(SubnetId=subnet['SubnetId'])

        # Delete Network Interfaces
        for eni in client.describe_network_interfaces()['NetworkInterfaces']:
            print(f"Deleting ENI: {eni['NetworkInterfaceId']}")
            client.delete_network_interface(NetworkInterfaceId=eni['NetworkInterfaceId'])

        # Delete VPCs
        for vpc in client.describe_vpcs()['Vpcs']:
            print(f"Deleting VPC: {vpc['VpcId']}")
            client.delete_vpc(VpcId=vpc['VpcId'])

    except ClientError as e:
        print(f"Skipping Network Resources: {e}")

def main():
    print(f"Starting full cleanup in {REGION} (excluding IAM)...")
    delete_cloudformation()
    delete_eks()
    delete_dynamodb()
    delete_secrets_manager()
    delete_s3()
    delete_load_balancers()
    delete_ec2()
    delete_rds()
    delete_lambda()
    delete_sqs()
    delete_sns()
    delete_network_resources()
    print("Full cleanup completed.")

if __name__ == "__main__":
    main()
