
__all__ = ['init_adapter', 'get_current_images_on_ecs', 'get_latest_images_from_ecr_registry']


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