from itertools import chain
import boto3
from typing import Set
from collections import namedtuple, defaultdict

EC2Url = namedtuple('EC2Url', ['url', 'instance_id'])


def get_ec2_urls(ec2_client) -> Set[EC2Url]:
    """
    Returns a collection of EC2 instances URL addresses
    which exposed to the internet.
    param ec2_client: botocore.client.EC2
    """
    urls = set()
    resevs = list(chain(*(page['Reservations']
                          for page in ec2_client.get_paginator('describe_instances').paginate(
        Filters=[
            {
                'Name': 'instance-state-name',
                'Values': ['running']
            }
        ]))))

    group_ids_to_instances = defaultdict(list)
    for instances in resevs:
        for instance_data in instances['Instances']:
            i_id = instance_data['InstanceId']
            for network_inr in instance_data['NetworkInterfaces']:
                association = network_inr.get('Association')
                if not association:
                    continue
                public_ip = association.get('PublicIp')
                if public_ip is None:
                    continue # only collect public ip addresses
                for group in network_inr.get('Groups', []):
                    group_ids_to_instances[group['GroupId']].append((public_ip, i_id))

    group_ids_to_instances = dict(group_ids_to_instances)
    if not group_ids_to_instances:
        return urls
    sec_groups = list(
        chain(*(page['SecurityGroups']
                for page in ec2_client.get_paginator('describe_security_groups').paginate(
            GroupIds=list(group_ids_to_instances.keys())
        ))))
    for sec in sec_groups:
        for ip_prem in sec['IpPermissions']:
            if ip_prem.get('FromPort') == '-1' or ip_prem.get('IpProtocol') == '-1':
                continue  # we can skip DHCP related rules
            for ip_range in ip_prem['IpRanges']:
                if ip_range['CidrIp'] == "0.0.0.0/0":
                    for ec2_info in group_ids_to_instances[sec['GroupId']]:
                        urls.add(EC2Url(f'http://{ec2_info[0]}:{ip_prem["FromPort"]}/',
                                           ec2_info[1]))
                        urls.add(EC2Url(f'https://{ec2_info[0]}:{ip_prem["FromPort"]}/',
                                           ec2_info[1]))
    return urls
