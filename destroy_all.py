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
            print(f"Deleting CloudFormation Stack: {stack['StackName']}")
            client.delete_stack(StackName=stack['StackName'])
    except ClientError as e:
        print(f"Skipping CloudFormation: {e}")

def delete_eks():
    client = boto3.client('eks', region_name=REGION)
    try:
        clusters = client.list_clusters()['clusters']
        for cluster in clusters:
            print(f"Deleting EKS Cluster: {cluster}")
            client.delete_cluster(name=cluster)
    except ClientError as e:
        print(f"Skipping EKS: {e}")

def delete_dynamodb():
    client = boto3.client('dynamodb', region_name=REGION)
    try:
        tables = client.list_tables()['TableNames']
        for table in tables:
            print(f"Deleting DynamoDB Table: {table}")
            client.delete_table(TableName=table)
    except ClientError as e:
        print(f"Skipping DynamoDB: {e}")

def delete_secrets_manager():
    client = boto3.client('secretsmanager', region_name=REGION)
    try:
        secrets = client.list_secrets()['SecretList']
        for secret in secrets:
            print(f"Deleting Secret: {secret['Name']}")
            client.delete_secret(SecretId=secret['ARN'], ForceDeleteWithoutRecovery=True)
    except ClientError as e:
        print(f"Skipping Secrets Manager: {e}")

def delete_s3():
    s3 = boto3.resource('s3', region_name=REGION)
    for bucket in s3.buckets.all():
        try:
            print(f"Emptying and Deleting Bucket: {bucket.name}")
            bucket.objects.all().delete()
            bucket.object_versions.all().delete()
            bucket.delete()
        except ClientError as e:
            print(f"Skipping S3 Bucket {bucket.name}: {e}")

def delete_load_balancers():
    elb = boto3.client('elbv2', region_name=REGION)
    try:
        lbs = elb.describe_load_balancers()['LoadBalancers']
        for lb in lbs:
            print(f"Deleting Load Balancer: {lb['LoadBalancerArn']}")
            elb.delete_load_balancer(LoadBalancerArn=lb['LoadBalancerArn'])
    except ClientError as e:
        print(f"Skipping Load Balancers: {e}")

    try:
        tgs = elb.describe_target_groups()['TargetGroups']
        for tg in tgs:
            print(f"Deleting Target Group: {tg['TargetGroupArn']}")
            elb.delete_target_group(TargetGroupArn=tg['TargetGroupArn'])
    except ClientError as e:
        print(f"Skipping Target Groups: {e}")

def delete_ec2():
    client = boto3.client('ec2', region_name=REGION)

    # Terminate instances
    try:
        instances = client.describe_instances()['Reservations']
        for res in instances:
            for inst in res['Instances']:
                print(f"Terminating Instance: {inst['InstanceId']}")
                client.terminate_instances(InstanceIds=[inst['InstanceId']])
    except ClientError as e:
        print(f"Skipping Instances: {e}")

    # Delete key pairs
    try:
        for kp in client.describe_key_pairs()['KeyPairs']:
            print(f"Deleting Key Pair: {kp['KeyName']}")
            client.delete_key_pair(KeyName=kp['KeyName'])
    except ClientError as e:
        print(f"Skipping Key Pairs: {e}")

    # Release Elastic IPs
    try:
        for eip in client.describe_addresses()['Addresses']:
            if 'AllocationId' in eip:
                print(f"Releasing Elastic IP: {eip['AllocationId']}")
                client.release_address(AllocationId=eip['AllocationId'])
            elif 'PublicIp' in eip:
                print(f"Releasing Elastic IP: {eip['PublicIp']}")
                client.release_address(PublicIp=eip['PublicIp'])
    except ClientError as e:
        print(f"Skipping Elastic IPs: {e}")

def delete_networking():
    client = boto3.client('ec2', region_name=REGION)

    # Detach and delete Internet Gateways
    try:
        igws = client.describe_internet_gateways()['InternetGateways']
        for igw in igws:
            for attachment in igw.get('Attachments', []):
                client.detach_internet_gateway(InternetGatewayId=igw['InternetGatewayId'], VpcId=attachment['VpcId'])
            print(f"Deleting Internet Gateway: {igw['InternetGatewayId']}")
            client.delete_internet_gateway(InternetGatewayId=igw['InternetGatewayId'])
    except ClientError as e:
        print(f"Skipping Internet Gateways: {e}")

    # Delete subnets
    try:
        subnets = client.describe_subnets()['Subnets']
        for sn in subnets:
            print(f"Deleting Subnet: {sn['SubnetId']}")
            client.delete_subnet(SubnetId=sn['SubnetId'])
    except ClientError as e:
        print(f"Skipping Subnets: {e}")

    # Delete route tables (except main)
    try:
        rts = client.describe_route_tables()['RouteTables']
        for rt in rts:
            if not any(assoc.get('Main', False) for assoc in rt.get('Associations', [])):
                print(f"Deleting Route Table: {rt['RouteTableId']}")
                client.delete_route_table(RouteTableId=rt['RouteTableId'])
    except ClientError as e:
        print(f"Skipping Route Tables: {e}")

    # Delete security groups (except default)
    try:
        sgs = client.describe_security_groups()['SecurityGroups']
        for sg in sgs:
            if sg['GroupName'] != 'default':
                print(f"Deleting Security Group: {sg['GroupId']}")
                client.delete_security_group(GroupId=sg['GroupId'])
    except ClientError as e:
        print(f"Skipping Security Groups: {e}")

    # Delete VPCs
    try:
        vpcs = client.describe_vpcs()['Vpcs']
        for vpc in vpcs:
            print(f"Deleting VPC: {vpc['VpcId']}")
            client.delete_vpc(VpcId=vpc['VpcId'])
    except ClientError as e:
        print(f"Skipping VPCs: {e}")

def main():
    print(f"Starting full cleanup in {REGION} (excluding IAM)...")
    delete_cloudformation()
    delete_eks()
    delete_dynamodb()
    delete_secrets_manager()
    delete_s3()
    delete_load_balancers()
    delete_ec2()
    delete_networking()
    print("Cleanup completed.")

if __name__ == "__main__":
    main()
