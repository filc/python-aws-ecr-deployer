
__all__ = [
    'init_adapter', 'get_current_images_on_ecs', 'get_latest_images_from_ecr_registry',
    'get_s3_file', 'get_images_by_repository', 'delete_images_from_repository',
    'get_ecs_clusters'
]


def init_adapter(cn):
    pass


def get_current_images_on_ecs(cn, cluster, region=''):
    return {
        'first_image': ('v23', 'service_name'),
        'second_image': ('v23', 'service_name'),
        'third_image': ('other-branchv25', 'service_name')
    }


def get_latest_images_from_ecr_registry(cn, registry_id, region=''):
    return {
        'fake_repo_name': ('v3', ),
        'second_image': ('v23', ),
        'third_image': ('v25', )
    }


def get_s3_file(cn, bucket, key, region='us-east-1'):
    if key == 'dummy_scotty.yml':
        with open('data/dummy_scotty.yml', 'rb') as f:
            return f.read()

    return b'fake content'


def get_images_by_repository(cn, repository, region='us-east-1', ecr_client=None):
    return [
        {'imageDigest': 'alnsdigaja', 'imageTag': 'v11'},
        {'imageDigest': 'alnsdixcfv', 'imageTag': 'v13'},
        {'imageDigest': 'alnsdierty', 'imageTag': 'latest'},
        {'imageDigest': 'alnsdvdfvd', 'imageTag': ''},
        {'imageDigest': 'alnsdigdff', 'imageTag': ''},
    ]


def delete_images_from_repository(cn, repository, image_digests, region='us-east-1'):
    return {'imageIds': [{'imageDigest': digest} for digest in image_digests], 'failures': []}


def get_ecs_clusters(cn, region='us-east-1'):
    return [
        {'clusterArn': 'arn:staging', 'clusterName': 'staging'},
        {'clusterArn': 'arn:production', 'clusterName': 'production'},
        {'clusterArn': 'arn:cluster3', 'clusterName': 'cluster3'}
    ]
