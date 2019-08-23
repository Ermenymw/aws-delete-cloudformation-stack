import time
from pprint import pprint
import boto3
import botocore

def process():
    stack_name="sl-blood-sample-specimen-dev"
    
    cf = boto3.client('cloudformation')

    exist_check = check_stack_existence(stack_name, cf)
    stack_sg_list = []
    if exist_check:
        stack_sg_list = check_stack_sg_resource(stack_name, cf)
        print(stack_sg_list)
        
        if stack_sg_list:
            for i in range(0, len(stack_sg_list)):
                sg_id = stack_sg_list[i]
                print(sg_id)
                delete_network_interface(sg_id)
        delete_stack(stack_name, cf)
        confirm_deletion(stack_name, cf)
        



def check_stack_existence(stack_name, cloudformation_season):
    try:
        stack_dict = cloudformation_season.describe_stacks(StackName=stack_name)
        print("=============STACK EXISTENCE=================")
        print("stack found")
        return True
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "ValidationError":
            print("Stack not found in SDRAD CloudFormation")
        else:
            print("Error type: {}".format(e.response['Error']['Code']))

def check_stack_sg_resource(stack_name, cloudformation_season):
    stack_sg_list = []
    print("=============SG EXISTENCE=================")
    try:
        stack_resource_dict = cloudformation_season.describe_stack_resource(
            StackName=stack_name,
            LogicalResourceId='ServiceSecGroup'
        )
        pprint(stack_resource_dict)
        stack_sg_list.append(stack_resource_dict['StackResourceDetail']['PhysicalResourceId'])
        
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "ValidationError":
            print("not found")
        else:
            print("Error type: {}".format(e.response['Error']['Code']))
    return stack_sg_list

def delete_network_interface(sg_id):
    print("=============NETWORK INTERFACE=================")
    client = boto3.client('ec2')
    response = client.describe_network_interfaces(
        Filters=[
            {
                'Name': 'group-id',
                'Values': [
                    sg_id,
                ]
            },
        ]
    )
    pprint(response['NetworkInterfaces'])
    for i in range(0, len(response['NetworkInterfaces'])):
        if 'Attachment' in response['NetworkInterfaces'][i]:
            try:
                attachmentId = response['NetworkInterfaces'][i]['Attachment']['AttachmentId']
                print(attachmentId)
                print("Detaching network interface attachment...")
                response1 = client.detach_network_interface(
                    AttachmentId=attachmentId
                )
            except botocore.exceptions.ClientError as e:
                print(e)
                print("Detaching failed")
        else:
            print("Dont have attachment")
        

        networkInterfaceId = response['NetworkInterfaces'][i]['NetworkInterfaceId']
        print(networkInterfaceId)
        print("Deleting network interface...")
        time.sleep(20)
        try:
            response2 = client.delete_network_interface(
                NetworkInterfaceId=networkInterfaceId
            )
        except botocore.exceptions.ClientError as e:
            print(e)
        print("response2: " + str(response2))
        
        
def delete_stack(stack_name, cloudformation_season):
    print("=============STACK DELETION=================")
    delete_stack_response = cloudformation_season.delete_stack(StackName=stack_name)
    if 'ResponseMetadata' in delete_stack_response and delete_stack_response['ResponseMetadata']['HTTPStatusCode'] < 300:
        print("Initializing stack deletion, deletion in progress!")
    else:
        print("11111: There was an Unexpected error, fail to delete {}.".format(stack_name))


def confirm_deletion(stack_name, cloudformation_season):
    time.sleep(20)
    print("=============STACK DELETION CONFIRMATION=================")
    try:
        stack_dict = cloudformation_season.describe_stacks(StackName=stack_name)
        print(stack_dict['Stacks'][0]['StackStatus'])
        if 'StackStatusReason' in stack_dict['Stacks'][0]:
            print(stack_dict['Stacks'][0]['StackStatusReason'])
        print("2222: There was an Unexpected error, fail to delete ".format(stack_name))
    except botocore.exceptions.ClientError:
        print("{} successfully deleted.".format(stack_name))


process()
