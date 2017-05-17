import boto3
import botocore
import re

__all__ = [
    'init_adapter', 'get_current_images_on_ecs', 'get_latest_images_from_ecr_registry',
    'get_s3_file', 'get_images_by_repository', 'delete_images_from_repository',
    'get_ecs_clusters'
]


def init_adapter(cn):
    pass


def get_current_images_on_ecs(cn, cluster, region='us-east-1'):
    ''' Returns with the images currently running on an ecs cluster.

    :param cluster: name of the ecs cluster
    :type cluster: str
    :param region: aws region
    :type region: str

    :return: dict
    '''

    ecs_client = boto3.client('ecs', region_name=region)
    current_images = {}

    services = _get_all_services_on_ecs(ecs_client, cluster)
    for service in services:
        last_parts = service['image'].split('/', 1)[-1].split(':')

        image_name = last_parts[0]
        image_tag = last_parts[1]
        tag_parts = re.search(r'v([0-9]+)$', image_tag)

        service_data = (image_tag, service['name'])

        if image_name in current_images:
            current_images[image_name].append(service_data)
        else:
            current_images.update({image_name: [service_data]})

    return current_images


def get_latest_images_from_ecr_registry(cn, registry_id, region='us-east-1'):
    ''' Returns with the latest images in the ecr (registry).

    :param registry_id: id of the ecr registry
    :type registry_id: str
    :param region: aws region
    :type region: str

    :return: dict
    '''
    ecr_client = boto3.client('ecr', region_name=region)

    latest_images = {}
    repositories = _get_all_resources(ecr_client.describe_repositories, 'repositories', registryId=registry_id)

    for repo in repositories:
        images = get_images_by_repository(cn, repo['repositoryName'], ecr_client=ecr_client, region=region)
        latest_images.update({repo['repositoryName']: (_get_latest_version(images), )})

    return latest_images


def get_s3_file(cn, bucket, key, region='us-east-1'):
    ''' Returns with a content of an s3 file.

    :param bucket: bucket name
    :type bucket: str
    :param key: s3 object key
    :type key: str
    :param region: aws region
    :type region: str

    :return: bytes
    '''

    client = boto3.client('s3', region_name=region)
    s3_object = client.get_object(Bucket=bucket, Key=key)
    return s3_object['Body'].read()


def get_images_by_repository(cn, repository, region='us-east-1', ecr_client=None):
    ''' Returns with all images of the given repository

    :param repository: repository name
    :type repository: str
    :param region: aws region
    :type region: str
    :param ecr_client: boto3 client for ecr
    :type region: obj

    :return: list
    '''
    if not ecr_client:
        ecr_client = boto3.client('ecr', region_name=region)

    try:
        return _get_all_resources(ecr_client.list_images, 'imageIds', repositoryName=repository)
    except botocore.exceptions.ClientError as e:
        return []

    return []


def delete_images_from_repository(cn, repository, image_digests, region='us-east-1'):
    ''' Removes the given images from the ecr repositories

    :param repository: repository name
    :type repository: str
    :param image_digests: digest hash of the images
    :type image_digests: list
    :param region: aws region
    :type region: str

    :return: list
    '''
    ecr_client = boto3.client('ecr', region_name=region)
    responses = []

    start_idx = 0
    while start_idx < len(image_digests):
        response = ecr_client.batch_delete_image(
            registryId=cn.g_('app_config').get('ecr_registry'),
            repositoryName=repository,
            imageIds=[
                {'imageDigest': digest} for digest in image_digests[start_idx:start_idx + 99]
            ]
        )

        responses.append(response)
        start_idx += 99

    return responses


def get_ecs_clusters(cn, region='us-east-1'):
    ''' Get the ECS clusters from the current account.

    :param region: aws region
    :type region: str

    :return: list
    '''
    ecs_client = boto3.client('ecs', region_name=region)
    expected_fields = ('clusterArn', 'clusterName')

    cluster_response = ecs_client.describe_clusters(
        clusters=_get_all_resources(ecs_client.list_clusters, 'clusterArns')
    )

    if not cluster_response:
        return []

    clusters = [
        {k: v for k, v in cluster.items() if k in expected_fields}
        for cluster in cluster_response['clusters']
    ]

    return clusters


def _get_latest_version(images):
    latest_version = 0

    for image in images:
        matches = re.search(r'^v([0-9]+)$', image.get('imageTag', ''))

        if matches and latest_version < int(matches.group(1)):
            latest_version = int(matches.group(1))

    return 'v{}'.format(latest_version)


def _get_all_services_on_ecs(client, cluster):
    services = []

    tasks = _get_tasks(client, cluster)
    for task in tasks.get('tasks', []):
        service = client.describe_task_definition(taskDefinition=task['taskDefinitionArn'])['taskDefinition']['containerDefinitions'][0]
        services.append(service)

    return services


def _get_tasks(client, cluster):
    task_arns = _get_all_resources(client.list_tasks, 'taskArns', maxResults=100, cluster=cluster)

    if task_arns:
        return client.describe_tasks(cluster=cluster, tasks=task_arns)

    return {}


def _get_all_resources(fn, field_name, **kwargs):
    resources = []
    next_token = ''

    while isinstance(next_token, str):
        if next_token:
            kwargs.update({'nextToken': next_token})

        partial_result = fn(**kwargs)
        if partial_result.get(field_name):
            resources += partial_result[field_name]

        next_token = partial_result.get('nextToken')

    return resources
