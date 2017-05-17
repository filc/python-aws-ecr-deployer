import logging
from .commons import ImageStatuses
import re

logger = logging.getLogger(__name__)


def compare_image_versions(ecs_images, ecr_images):

    def _get_result(ecr_version, ecs_version, result_text):
        return {
            'ecr_version': ecr_version,
            'ecs_version': ecs_version,
            'result': result_text
        }

    def _extend_result_with_only_ecs_images(compare_result):
        compare_result.update({
            ecs_image: _get_result('', _get_ecs_tag_from_services(ecs_info)[1], ImageStatuses.ONLY_IN_ECS)
            for ecs_image, ecs_info in ecs_images.items() if ecs_image not in ecr_images
        })

    def _get_ecs_tag_from_services(services):
        ecs_tags = [s[0] for s in services]

        if len(ecs_tags) > 1:
            ecs_display_tag = ','.join(['::'.join(s) for s in services])
        else:
            ecs_display_tag = '::'.join(services[0])

        if len(set(ecs_tags)) == 1:
            ecs_tag = ecs_tags[0]
            single_version = True
        else:
            single_version = False
            ecs_tag = ecs_display_tag

        return ecs_tag, ecs_display_tag, single_version

    compare_result = {}

    for ecr_image, ecr_info in ecr_images.items():
        ecr_tag = ecr_info[0]
        ecs_tag, ecs_display_tag, single_ecs_version = _get_ecs_tag_from_services(ecs_images.get(ecr_image, [['']]))

        if not single_ecs_version:
            compare_result[ecr_image] = _get_result(ecr_tag, ecs_display_tag, ImageStatuses.MORE_VERSIONS_IN_ECS)
        else:
            ecs_version = re.search(r'v([0-9]+)$', ecs_tag)
            ecs_version = int(ecs_version.group(1)) if ecs_version else 0

            ecr_version = re.search(r'v([0-9]+)$', ecr_tag)
            ecr_version = int(ecr_version.group(1)) if ecr_version else 0

            if ecs_tag and ecs_tag != 'v{}'.format(ecs_version):
                result_text = ImageStatuses.OTHER_BRANCH_IN_ECS
            elif ecr_image not in ecs_images:
                result_text = ImageStatuses.ONLY_IN_ECR
            elif ecr_version == ecs_version:
                result_text = ImageStatuses.UP_TO_DATE
            elif ecr_version > ecs_version:
                result_text = ImageStatuses.GREATER_IN_ECR
            elif ecr_version < ecs_version:
                result_text = ImageStatuses.GREATER_IN_ECS

            compare_result[ecr_image] = _get_result(ecr_tag, ecs_display_tag, result_text)

    _extend_result_with_only_ecs_images(compare_result)
    return compare_result
