from functools import wraps
import json
from flask import Blueprint, g, render_template, make_response, request
from .commons import ImageStatuses
import base64


bp = Blueprint('controllers', __name__, template_folder='templates', static_folder='static')


def _return_json(fn):
    @wraps(fn)
    def inner_fn(*args, **kwargs):
        response = make_response(json.dumps(fn(*args, **kwargs)))
        response.headers['Content-Type'] = 'application/json'
        return response
    return inner_fn


@bp.route("/", methods=['GET'])
def index():
    auth = request.authorization
    basic_auth = '' if not auth else base64.b64encode(bytes(':'.join([auth.username, auth.password]), 'utf-8')).decode('utf-8')
    return render_template('index.html', base_url=g.cn.g_('app_config').get('base_url'), basic_auth=basic_auth)


@bp.route("/ecr-repository/<path:repository>", methods=['GET'])
def ecr_repository(repository):
    auth = request.authorization
    basic_auth = '' if not auth else base64.b64encode(bytes(':'.join([auth.username, auth.password]), 'utf-8')).decode('utf-8')
    return render_template('ecr_repository.html', base_url=g.cn.g_('app_config').get('base_url'), basic_auth=basic_auth, repository=repository)


@bp.route("/status", methods=['GET'])
@_return_json
def status():
    classes = {
        ImageStatuses.UP_TO_DATE: 'success',
        ImageStatuses.ONLY_IN_ECR: 'warning',
        ImageStatuses.GREATER_IN_ECR: 'warning',
        ImageStatuses.GREATER_IN_ECS: 'danger',
        ImageStatuses.ONLY_IN_ECS: 'danger',
        ImageStatuses.OTHER_BRANCH_IN_ECS: 'warning'
    }

    texts = {
        ImageStatuses.UP_TO_DATE: 'Up-to-date',
        ImageStatuses.ONLY_IN_ECR: 'Only in ECR',
        ImageStatuses.GREATER_IN_ECR: 'Not the latest',
        ImageStatuses.GREATER_IN_ECS: 'What???',
        ImageStatuses.ONLY_IN_ECS: 'Only on ECS',
        ImageStatuses.OTHER_BRANCH_IN_ECS: 'Other branch on ECS'
    }

    config = g.cn.g_('app_config')
    status = g.cn.f_('core.get_status', config.get('ecs_cluster'), config.get('ecr_registry'))

    formatted = [
        {
            'image_name': image,
            'ecs_version': str(info['ecs_version']),
            'ecr_version': info['ecr_version'],
            'status_text': texts[info['result']],
            'status_class': classes[info['result']],
            'details_link': '{}/ecr-repository/{}'.format(g.cn.g_('app_config').get('base_url'), image)
        } for image, info in status.items()
    ]

    return formatted


@bp.route("/ecr-repository-versions/<path:repository>", methods=['GET'])
@_return_json
def ecr_repository_versions(repository):
    data = [
        {
            'tag': version.get('imageTag', ''),
            'digest': version.get('imageDigest', '')
        } for version in g.cn.f_('aws.get_images_by_repository', repository)
    ]

    return data


@bp.route("/delete_images", methods=['POST'])
@_return_json
def delete_images():
    params = request.get_json()

    if not params.get('images'):
        return [{'success': False, 'title': 'Nothing happened', 'result': 'No images given'}]

    result = g.cn.f_(
        'aws.delete_images_from_repository',
        repository=params['repository'],
        image_digests=params['images'],
        region=g.cn.g_('app_config').get('ecr_region')
    )

    return [{'success': True, 'title': 'Deletion result', 'result': json.dumps(result)}]


@bp.route("/deploy", methods=['POST'])
@_return_json
def deploy():
    return g.cn.f_('core.deploy_images', images=request.get_json())
