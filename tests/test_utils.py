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
            {'image': ('v13', )},
            {'image': [('v13', '')]},
            {
                'image': {
                    'ecr_version': 'v13',
                    'ecs_version': 'v13',
                    'result': ImageStatuses.UP_TO_DATE
                }
            }
        ],
        [
            {'image': ('v13', )},
            {},
            {
                'image': {
                    'ecr_version': 'v13',
                    'ecs_version': '',
                    'result': ImageStatuses.ONLY_IN_ECR
                }
            }
        ],
        [
            {'image': ('v13', )},
            {'image': [('v11', '')]},
            {
                'image': {
                    'ecr_version': 'v13',
                    'ecs_version': 'v11',
                    'result': ImageStatuses.GREATER_IN_ECR
                }
            }
        ],
        [
            {'image': ('v11', )},
            {'image': [('v13', '')]},
            {
                'image': {
                    'ecr_version': 'v11',
                    'ecs_version': 'v13',
                    'result': ImageStatuses.GREATER_IN_ECS
                }
            }
        ],
        [
            {},
            {'image': [('v13', '')]},
            {
                'image': {
                    'ecr_version': '',
                    'ecs_version': 'v13',
                    'result': ImageStatuses.ONLY_IN_ECS
                }
            }
        ],
        [
            {'image': ('v13', )},
            {'image': [('v13', ''), ('v13', '')]},
            {
                'image': {
                    'ecr_version': 'v13',
                    'ecs_version': 'v13',
                    'result': ImageStatuses.UP_TO_DATE
                }
            }
        ],
        [
            {'image': ('v13', )},
            {'image': [('v13', 'service_1'), ('v13', 'service_3'), ('v14', 'service_3'), ('v15', 'service_5')]},
            {
                'image': {
                    'ecr_version': 'v13',
                    'ecs_version': 'v13::service_1,v13::service_3,v14::service_3,v15::service_5',
                    'result': ImageStatuses.MORE_VERSIONS_IN_ECS,
                }
            }
        ],
        [
            {},
            {'image': [('v13', 'service_1'), ('v13', 'service_3'), ('v14', 'service_3'), ('v15', 'service_5')]},
            {
                'image': {
                    'ecr_version': '',
                    'ecs_version': 'v13::service_1,v13::service_3,v14::service_3,v15::service_5',
                    'result': ImageStatuses.ONLY_IN_ECS,
                }
            }
        ]
    ]

    [_test_compare_image_versions(case[0], case[1], case[2]) for case in cases]


def _test_compare_image_versions(ecr_images, ecs_images, expected_result):
    assert expected_result == utils.compare_image_versions(ecs_images, ecr_images)
