import boto3


__all__ = ['init_adapter', 'get_current_images_on_ecs', 'get_latest_images_from_ecr_registry', 'get_s3_file']


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
        if last_parts[1][0] == 'v':
            version = int(last_parts[1][1:])
            current_images.update({image_name: (version, service['name'])})

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
        images = _get_all_resources(ecr_client.list_images, 'imageIds', repositoryName=repo['repositoryName'])
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


def _get_latest_version(images):
    latest_version = 0
    for image in images:
        version = image.get('imageTag', '')[1:]

        try:
            if latest_version < int(version):
                latest_version = int(version)
        except ValueError:
            pass

    return latest_version


def _get_all_services_on_ecs(client, cluster):
    services = []
    images = []

    tasks = _get_tasks(client, cluster);
    for task in tasks['tasks']:
        service = client.describe_task_definition(taskDefinition=task['taskDefinitionArn'])['taskDefinition']['containerDefinitions'][0]
        if service['image'] not in images:
            services.append(service)
            images.append(service['image'])
            # print(service['image'])

    return services


def _get_tasks(client, cluster):
    task_arns = _get_all_resources(client.list_tasks, 'taskArns', maxResults=100, cluster=cluster)
    return client.describe_tasks(cluster=cluster, tasks=task_arns)


def _get_all_resources(fn, field_name, **kwargs):
    resources = []
    next_token = ''

    while isinstance(next_token, str):
        if next_token:
            kwargs.update({'nextToken': next_token})

        partial_result = fn(**kwargs)
        resources += partial_result[field_name]
        next_token = partial_result.get('nextToken')

    return resources
