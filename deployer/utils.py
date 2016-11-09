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
            ecs_image: _get_result('', ecs_info[0], ImageStatuses.ONLY_IN_ECS)
            for ecs_image, ecs_info in ecs_images.items() if ecs_image not in ecr_images
        })

    compare_result = {}

    for ecr_image, ecr_info in ecr_images.items():
        ecs_tag = ecs_images.get(ecr_image, [''])[0]
        ecr_tag = ecr_info[0]

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

        compare_result[ecr_image] = _get_result(ecr_tag, ecs_tag, result_text)

    _extend_result_with_only_ecs_images(compare_result)
    return compare_result
