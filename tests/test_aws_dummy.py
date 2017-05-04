import mock
import pytest
from deployer import aws_dummy as aws


def test_init_adapter_is_callable():
    aws.init_adapter({})
    assert True


def test_get_latest_images_from_ecr_registry():
    images = aws.get_latest_images_from_ecr_registry({}, 'fake_registry_id')

    assert images == {
        'fake_repo_name': ('v3', ),
        'second_image': ('v23', ),
        'third_image': ('v25', )
    }


def test_get_current_images_on_ecs():
    images = aws.get_current_images_on_ecs({}, 'fake_region')

    assert images == {
        'first_image': ('v23', 'service_name'),
        'second_image': ('v23', 'service_name'),
        'third_image': ('other-branchv25', 'service_name')
    }


def test_get_s3_file(monkeypatch):
    content = aws.get_s3_file({}, bucket="", key="")
    assert content == b'fake content'


def test_get_s3_file_dummy_yml(monkeypatch):
    content = aws.get_s3_file({}, bucket="", key="dummy_scotty.yml")
    assert len(content) == 824


def test_get_images_by_repository(monkeypatch):
    content = aws.get_images_by_repository({}, repository='asda')
    assert content[0]['imageDigest'] == 'alnsdigaja'
    assert content[0]['imageTag'] == 'v11'
    assert len(content) == 5


def test_delete_images_from_repository():
    result = aws.delete_images_from_repository({}, repository='fake_rep', image_digests=['asda'])
    assert result == {'imageIds': [{'imageDigest': 'asda'}], 'failures': []}


def test_get_ecs_clusters():
    result = aws.get_ecs_clusters({})
    assert result == [
        {'clusterArn': 'arn:staging', 'clusterName': 'staging'},
        {'clusterArn': 'arn:production', 'clusterName': 'production'},
        {'clusterArn': 'arn:cluster3', 'clusterName': 'cluster3'}
    ]
