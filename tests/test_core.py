import os
import pytest
import mock
from hexconnector import HexConnector


@pytest.fixture
def cn():
    cn = HexConnector()

    cn.s_('app_config', {
        'default_region': '',
        'ecs_cluster': 'staging',
        'scotty_yml_s3_key': 'dummy_scotty.yml',
        'base_dir': os.path.dirname(os.path.realpath(__file__)) + '/..'
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


def test_deploy_images_error(cn, monkeypatch):
    fake_popen = mock.MagicMock()
    fake_popen.communicate = mock.MagicMock(return_value=(b'', b'Error...'))
    monkeypatch.setattr('deployer.core.Popen', mock.MagicMock(return_value=fake_popen))

    result = cn.f_('core.deploy_images', {'image1': 23})

    assert {'version': 23, 'result': 'Error...', 'success': False, 'cluster': 'staging', 'service': 'service1'} in result
    assert {'version': 23, 'result': 'Error...', 'success': False, 'cluster': 'staging', 'service': 'service2'} in result


def test_deploy_images_success(cn, monkeypatch):
    fake_popen = mock.MagicMock()
    fake_popen.communicate = mock.MagicMock(return_value=(b'stdout...', b''))
    monkeypatch.setattr('deployer.core.Popen', mock.MagicMock(return_value=fake_popen))

    result = cn.f_('core.deploy_images', {'image1': 23})

    assert {'success': True, 'version': 23, 'service': 'service1', 'cluster': 'staging', 'result': 'stdout...'} in result
    assert {'success': True, 'version': 23, 'service': 'service2', 'cluster': 'staging', 'result': 'stdout...'} in result


def test_deploy_images_process_exception(cn, monkeypatch):

    def fake_communicate(*args, **kwargs):
        raise Exception('Error...')

    fake_popen = mock.MagicMock()
    fake_popen.communicate = fake_communicate
    monkeypatch.setattr('deployer.core.Popen', mock.MagicMock(return_value=fake_popen))

    result = cn.f_('core.deploy_images', {'image1': 23})

    assert {'success': False, 'version': 23, 'service': 'service1', 'cluster': 'staging', 'error': 'Error...'} in result
    assert {'success': False, 'version': 23, 'service': 'service2', 'cluster': 'staging', 'error': 'Error...'} in result
