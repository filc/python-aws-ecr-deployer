import pytest
from hexconnector import HexConnector


@pytest.fixture
def cn():
    cn = HexConnector()

    cn.s_('app_config', {
        'ecs_region': '',
        'ecr_region': ''
    })

    cn.register_adapter('core', 'deployer.core')
    cn.register_adapter('aws', 'deployer.aws_dummy')
    return cn


def test_get_status(cn):
    status = cn.f_('core.get_status', 'fake', 'fake')

    assert status['second_image'] == {
        'ecs_version': 23,
        'ecr_version': 23,
        'result': 'UP_TO_DATE'
    }
