
__all__ = ['init_adapter', 'get_current_images_on_ecs', 'get_latest_images_from_ecr_registry', 'get_s3_file']


def init_adapter(cn):
    pass


def get_current_images_on_ecs(cn, cluster, region=''):
    return {
        'first_image': (23, 'service_name'),
        'second_image': (23, 'service_name')
    }


def get_latest_images_from_ecr_registry(cn, registry_id, region=''):
    return {
        'fake_repo_name': (3, ),
        'second_image': (23, )
    }


def get_s3_file(cn, bucket, key, region='us-east-1'):
    if key == 'dummy_scotty.yml':
        with open('data/dummy_scotty.yml', 'r') as f:
            return f.read()

    return b'fake content'