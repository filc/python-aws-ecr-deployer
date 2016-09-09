import os
from deployer import utils
from deployer.commons import ImageStatuses


def test_compare_image_versions_empty_images():
    ecs_images = {}
    ecr_images = {}

    compare_result = utils.compare_image_versions(ecs_images, ecr_images)
    assert compare_result == {}


def test_compare_image_versions():
    cases = [
        [
            {'image': (13, )},
            {'image': (13, )},
            {
                'image': {
                    'ecr_version': 13,
                    'ecs_version': 13,
                    'result': ImageStatuses.UP_TO_DATE
                }
            }
        ],
        [
            {'image': (13, )},
            {},
            {
                'image': {
                    'ecr_version': 13,
                    'ecs_version': 0,
                    'result': ImageStatuses.ONLY_IN_ECR
                }
            }
        ],
        [
            {'image': (13, )},
            {'image': (11, )},
            {
                'image': {
                    'ecr_version': 13,
                    'ecs_version': 11,
                    'result': ImageStatuses.GREATER_IN_ECR
                }
            }
        ],
        [
            {'image': (11, )},
            {'image': (13, )},
            {
                'image': {
                    'ecr_version': 11,
                    'ecs_version': 13,
                    'result': ImageStatuses.GREATER_IN_ECS
                }
            }
        ],
        [
            {},
            {'image': (13, )},
            {
                'image': {
                    'ecr_version': 0,
                    'ecs_version': 13,
                    'result': ImageStatuses.ONLY_IN_ECS
                }
            }
        ]
    ]

    [_test_compare_image_versions(case[0], case[1], case[2]) for case in cases]


def _test_compare_image_versions(ecr_images, ecs_images, expected_result):
    assert expected_result == utils.compare_image_versions(ecs_images, ecr_images)
