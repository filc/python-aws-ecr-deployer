from . import utils


def init_adapter(cn):
    pass


def get_status(cn, ecs_cluster, ecr_registry_id):
    ecs_region = cn.g_('app_config').get('ecs_region')
    ecr_region = cn.g_('app_config').get('ecr_region')

    ecs_images = cn.f_('aws.get_current_images_on_ecs', ecs_cluster, region=ecs_region)
    ecr_images = cn.f_('aws.get_latest_images_from_ecr_registry', ecr_registry_id, region=ecr_region)

    return utils.compare_image_versions(ecs_images, ecr_images)