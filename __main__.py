import boto3
import argparse
import os

client = boto3.client('ecs')
ec2_client = boto3.client('ec2')

# Options
parser = argparse.ArgumentParser()
parser.add_argument('-c', '--cluster',
                    help='Specify ECS cluster')
parser.add_argument('-s', '--service',
                    help='Specify ECS service')
parser.add_argument('-u', '--user',
                    help='Specify connecting user')

args = parser.parse_args()


def get_client(service):
    """Get an AWS client for a service."""
    session = boto3.Session()
    return session.client(service)


def get_task():
    """Get ECS task."""
    tasks = client.list_tasks(
        cluster=args.cluster,
        serviceName=args.service
    )
    return tasks['taskArns'][0]


def describe_tasks():
    """Describe ECS task."""
    describe = client.describe_tasks(
        cluster=args.cluster,
        tasks=[
            get_task()
        ]
    )
    return describe['tasks'][0]['containerInstanceArn']


def container_id():
    """Describe container instances."""
    task = describe_tasks()
    instance = client.describe_container_instances(
        cluster=args.cluster,
        containerInstances=[
            task
        ]
    )
    return(instance['containerInstances'][0]['ec2InstanceId'])


def connect():
    """Connect to instance IP."""
    instance = ec2_client.describe_instances(InstanceIds=[container_id()])
    info = instance['Reservations'][0]['Instances'][0]
    priv = info['PrivateIpAddress']
    print('ssh {}@{}'.format(args.user, priv))
    os.system('ssh {}@{}'.format(args.user, priv))


def main(args=None):
    """The main routine."""
    connect()

if __name__ == "__main__":
    main()
