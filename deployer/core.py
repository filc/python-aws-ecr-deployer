import yaml
import logging
from subprocess import Popen, PIPE
from . import utils
import re

logger = logging.getLogger(__name__)


def init_adapter(cn):
    pass


def get_status(cn, ecs_cluster, ecr_registry_id):
    ''' Returns with the dict of the images that are on the ecs cluster and in the ecr registry.

    :param ecs_cluster: name of the ecs cluster
    :type ecs_cluster: str
    :param ecr_cluster: id of the ecr registry
    :type ecr_cluster: str

    :return dict
    '''
    app_config = cn.g_('app_config')

    ecs_images = cn.f_('aws.get_current_images_on_ecs', ecs_cluster, region=app_config.get('ecs_region'))
    ecr_images = cn.f_('aws.get_latest_images_from_ecr_registry', ecr_registry_id, region=app_config.get('ecr_region'))

    return utils.compare_image_versions(ecs_images, ecr_images)


def deploy_images(cn, images, cluster):
    ''' Deploy the given images with given version. Returns with the list of the results of the deployment.

    :param images: images with the versions
    :type images: dict

    :return list
    '''

    def _get_real_tag(tag):
        return 'v{}'.format(tag) if re.match(r'^[0-9]$', str(tag)) else tag

    # def _convert_to_int(x):
    #     return int(re.sub("[^0-9]", "", x) if isinstance(x, str) else x)

    _images = {image: _get_real_tag(tag) for image, tag in images.items() if _get_real_tag(tag)}

    services = _get_services_by_images(cn, _images) if _images else []
    return [_deploy_service(cn, service[0], service[1], cluster) for service in services]


def _deploy_service(cn, service, tag, cluster):
    process = Popen(
        [
            'scotty',
            '-c',
            '{}/data/scotty.yml'.format(cn.g_('app_config').get('base_dir')),
            'deploy',
            cluster,
            service,
            tag
        ],
        stdout=PIPE,
        stderr=PIPE
    )

    try:
        stdout, stderr = process.communicate(timeout=300)
    except Exception as e:
        logger.error(str(e))
        return {'success': False, 'title': service, 'version': tag, 'cluster': cluster, 'error': str(e)}

    if stderr:
        return {'success': False, 'title': service, 'version': tag, 'cluster': cluster, 'result': stderr.decode('utf-8')}

    return {'success': True, 'title': service, 'version': tag, 'cluster': cluster, 'result': stdout.decode('utf-8')}


def _get_services_by_images(cn, images):
    config = _get_service_config(cn)

    services = []
    if isinstance(config, dict) and config.get('services'):
        for service, info in config['services'].items():
            image_name = _get_image_name_from_docker_path(info['containers'][0]['image_path'])
            if image_name in images:
                services.append((service, images[image_name]))

    return services


def _get_service_config(cn):
    app_config = cn.g_('app_config')

    config_text = cn.f_(
        'aws.get_s3_file',
        bucket=app_config.get('scotty_yml_s3_bucket'),
        key=app_config.get('scotty_yml_s3_key'),
        region=app_config.get('s3_region')
    )

    with open('data/scotty.yml', 'w') as f:
        f.write(config_text.decode('utf-8'))

    return yaml.load(config_text)


def _get_image_name_from_docker_path(docker_path):
    if '/' in docker_path:
        return docker_path.split("/", 1)[1]

    return ''
