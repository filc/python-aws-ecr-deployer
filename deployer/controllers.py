import json
from flask import Blueprint, g, render_template
from .commons import ImageStatuses


bp = Blueprint('controllers', __name__, url_prefix='/', template_folder='templates')


@bp.route("/", methods=['GET'])
def index():
    config = g.cn.g_('app_config')

    data = {
        'classes': {
            ImageStatuses.UP_TO_DATE: 'success',
            ImageStatuses.ONLY_IN_ECR: 'warning',
            ImageStatuses.GREATER_IN_ECR: 'warning',
            ImageStatuses.GREATER_IN_ECS: 'danger',
            ImageStatuses.ONLY_IN_ECS: 'danger'
        },
        'texts': {
            ImageStatuses.UP_TO_DATE: 'Up-to-date',
            ImageStatuses.ONLY_IN_ECR: 'Only in ECR',
            ImageStatuses.GREATER_IN_ECR: 'Not the latest',
            ImageStatuses.GREATER_IN_ECS: 'What???',
            ImageStatuses.ONLY_IN_ECS: 'Only on ECS'
        },
        'status': g.cn.f_('core.get_status', config.get('ecs_cluster'), config.get('ecr_registry'))
    }

    return render_template('index.html', **data)
