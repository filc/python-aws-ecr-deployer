import mock
import pytest
from deployer import aws


@pytest.fixture
def fake_ecr_client(monkeypatch):
    fake_ecr_repositories = {
        'repositories': [
            {'repositoryName': 'fake_repo_name'}
        ]
    }

    fake_ecr_images = {
        'imageIds': [
            {'imageTag': 'v2'},
            {'imageTag': 'v3'},
            {'imageTag': 'latest'}
        ]
    }

    fake_client = mock.MagicMock()
    fake_client.describe_repositories = mock.MagicMock(return_value=fake_ecr_repositories)
    fake_client.list_images = mock.MagicMock(return_value=fake_ecr_images)

    monkeypatch.setattr('deployer.aws.boto3.client', mock.MagicMock(return_value=fake_client))
    return fake_client


@pytest.fixture
def fake_ecs_client(monkeypatch):
    fake_tasks = {
        'tasks': [
            {'taskDefinitionArn': 'first'},
            {'taskDefinitionArn': 'second'}
        ]
    }

    def fake_describe_task_definition(taskDefinition):
        return {
            'taskDefinition': {
                'containerDefinitions': [{
                    'image': 'address/{}_image:v23'.format(taskDefinition),
                    'name': 'service_name'
                }]
            }
        }

    fake_client = mock.MagicMock()
    fake_client.describe_tasks = mock.MagicMock(return_value=fake_tasks)
    fake_client.describe_task_definition = fake_describe_task_definition

    monkeypatch.setattr('deployer.aws.boto3.client', mock.MagicMock(return_value=fake_client))
    return fake_client


def test_init_adapter_is_callable():
    aws.init_adapter({})
    assert True


def test_get_latest_images_from_ecr_registry(fake_ecr_client):
    images = aws.get_latest_images_from_ecr_registry({}, 'fake_registry_id')
    assert images == {'fake_repo_name': ('v3', )}


def test_get_images_by_repository(fake_ecr_client):
    images = aws.get_images_by_repository({}, 'fake_repo')
    assert images == [
        {'imageTag': 'v2'},
        {'imageTag': 'v3'},
        {'imageTag': 'latest'}
    ]


def test_get_current_images_on_ecs(fake_ecs_client):
    images = aws.get_current_images_on_ecs({}, 'fake_region')

    assert images == {
        'first_image': ('v23', 'service_name'),
        'second_image': ('v23', 'service_name')
    }


def test_get_s3_file(monkeypatch):
    fake_body = mock.MagicMock()
    fake_body.read = mock.MagicMock(return_value=b'fake content')

    fake_client = mock.MagicMock()
    fake_client.get_object = mock.MagicMock(return_value=mock.MagicMock(return_value={'Body': fake_body})())

    monkeypatch.setattr('deployer.aws.boto3.client', mock.MagicMock(return_value=fake_client))

    content = aws.get_s3_file({}, bucket="", key="")

    assert content == b'fake content'


def test_delete_images_from_repository(monkeypatch):
    fake_client = mock.MagicMock()
    fake_client.batch_delete_image = mock.MagicMock()
    monkeypatch.setattr('deployer.aws.boto3.client', mock.MagicMock(return_value=fake_client))

    fake_cn = mock.MagicMock()
    fake_cn.g_ = mock.MagicMock(return_value={'ecr_registry': 'test'})

    result = aws.delete_images_from_repository(fake_cn, 'fake_rep', ['i1', 'i2'])
    fake_client.batch_delete_image.assert_called_with(
        imageIds=[{'imageDigest': 'i1'}, {'imageDigest': 'i2'}],
        registryId='test',
        repositoryName='fake_rep'
    )


def test_get_ecs_clusters(monkeypatch):
    fake_ecs_clusters = {
        'clusters': [
            {'clusterArn': 'arn1', 'clusterName': 'cluster1'},
            {'clusterArn': 'arn2', 'clusterName': 'cluster2'}
        ]
    }

    fake_ecs_cluster_list = {
        'clusterArns': []
    }

    fake_client = mock.MagicMock()
    fake_client.describe_clusters = mock.MagicMock(return_value=fake_ecs_clusters)
    fake_client.list_clusters = mock.MagicMock(return_value=fake_ecs_cluster_list)

    monkeypatch.setattr('deployer.aws.boto3.client', mock.MagicMock(return_value=fake_client))
    assert aws.get_ecs_clusters({}) == [{'clusterArn': 'arn1', 'clusterName': 'cluster1'}, {'clusterArn': 'arn2', 'clusterName': 'cluster2'}]


def test_get_ecs_clusters_empty(monkeypatch):
    fake_ecs_cluster_list = {}

    fake_client = mock.MagicMock()
    fake_client.list_clusters = mock.MagicMock(return_value=fake_ecs_cluster_list)
    monkeypatch.setattr('deployer.aws.boto3.client', mock.MagicMock(return_value=fake_client))

    assert aws.get_ecs_clusters({}) == []
