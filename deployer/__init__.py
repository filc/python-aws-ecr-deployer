import logging
import logging.config
from flask import Flask, current_app, g, abort, request
from hexconnector import HexConnector
from beaker.middleware import SessionMiddleware
from .controllers import bp

logger = logging.getLogger(__name__)


def create_app(config=None):
    app = Flask(__name__)
    app.config.update(config)
    app.wsgi_app = SessionMiddleware(app.wsgi_app, config['session'])
    app.register_blueprint(bp)

    if config.get('logger'):
        logging.config.dictConfig(config.get('logger'))

    _configure_error_handlers(app)
    _setup_requests(app)
    return app


def _setup_requests(app):

    def _init_request():
        session = request.environ['beaker.session']
        session.save()

        _setup_connector(
            app=current_app,
            app_config=current_app.config,
            session=session
        )

    @app.before_request
    def before_request():
        init_request = _init_request()
        return init_request


def _setup_connector(app, **kw):
    g.cn = HexConnector()

    for port, adapter in app.config['adapters'].items():
        g.cn.register_adapter(port, adapter)

    for k, v in kw.items():
        g.cn.s_(k, v)

    return g.cn


def _configure_error_handlers(app):

    @app.errorhandler(Exception)
    def handle_invalid_usage(error):
        logger.error(error, exc_info=True)
        return abort(500)
