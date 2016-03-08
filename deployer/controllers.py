from functools import wraps
import json
from flask import Blueprint, g, render_template, make_response, request
from .commons import ImageStatuses


bp = Blueprint('controllers', __name__, template_folder='templates')


def _return_json(fn):
    @wraps(fn)
    def inner_fn(*args, **kwargs):
        response = make_response(json.dumps(fn(*args, **kwargs)))
        response.headers['Content-Type'] = 'application/json'
        return response
    return inner_fn

@bp.route("/", methods=['GET'])
def index():
    return render_template('index.html')


@bp.route("/status", methods=['GET'])
@_return_json
def status():
    classes = {
        ImageStatuses.UP_TO_DATE: 'success',
        ImageStatuses.ONLY_IN_ECR: 'warning',
        ImageStatuses.GREATER_IN_ECR: 'warning',
        ImageStatuses.GREATER_IN_ECS: 'danger',
        ImageStatuses.ONLY_IN_ECS: 'danger'
    }

    texts = {
        ImageStatuses.UP_TO_DATE: 'Up-to-date',
        ImageStatuses.ONLY_IN_ECR: 'Only in ECR',
        ImageStatuses.GREATER_IN_ECR: 'Not the latest',
        ImageStatuses.GREATER_IN_ECS: 'What???',
        ImageStatuses.ONLY_IN_ECS: 'Only on ECS'
    }

    config = g.cn.g_('app_config')
    status = g.cn.f_('core.get_status', config.get('ecs_cluster'), config.get('ecr_registry'))

    formatted = [
        {
            'image_name': image,
            'ecs_version': info['ecs_version'],
            'ecr_version': info['ecr_version'],
            'status_text': texts[info['result']],
            'status_class': classes[info['result']]
        } for image, info in status.items()
    ]

    return formatted


@bp.route("/deploy", methods=['POST'])
@_return_json
def deploy():
    return g.cn.f_('core.deploy_images', images=request.get_json())
