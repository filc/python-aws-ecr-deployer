import os

base_url = os.environ.get('DP_BASE_URL', '')
base_dir = os.environ.get('DP_APP_ROOT', os.path.dirname(os.path.realpath(__file__)) + '/..')

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

default_region = os.environ.get('AWS_DEFAULT_REGION', None)

ecr_registry = os.environ.get('DP_ECR_REGISTRY', '')
ecs_region = os.environ.get('DP_ECS_REGION', default_region or 'us-east-1')
ecr_region = os.environ.get('DP_ECR_REGION', default_region or 'us-east-1')
s3_region = os.environ.get('DP_S3_REGION', default_region or 'us-east-1')

scotty_yml_s3_bucket = os.environ.get('DP_SCOTTY_YML_S3_BUCKET', None)
scotty_yml_s3_key = os.environ.get('DP_SCOTTY_YML_S3_KEY', None)
