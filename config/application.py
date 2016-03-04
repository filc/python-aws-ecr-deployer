import os

adapters = {
    'core': 'deployer.core',
    'aws': 'deployer.aws'
}

session = {
    'session.type': 'file',
    'session.cookie_expires': False,
    'session.data_dir': '/tmp/sessions',
    'session.httponly': True,
    'session.key': 'deployer.session.id'
}

ecs_cluster = os.environ.get('DP_ECS_CLUSTER', '')
ecr_registry = os.environ.get('DP_ECR_REGISTRY', '')
ecs_region = os.environ.get('DP_ECS_REGION', 'us-east-1')
ecr_region = os.environ.get('DP_ECR_REGION', 'us-east-1')