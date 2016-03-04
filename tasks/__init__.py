from invoke import run, task


@task
def precommit(config=None):
    run('py.test --cov-config .coveragerc --cov-report term-missing --cov deployer tests/ --junit-xml pytests.xml')

# def _init_connector(config=None):
#     from hexconnector import HexConnector
#     from lensa3.config import load_app_config

#     cn = HexConnector()

#     cn.s_('session', {})
#     cn.s_('app_config', load_app_config('l4c', override_cfg=config))

#     for port, adapter in cn.g_('app_config').get('adapters').items():
#       cn.register_adapter(port, adapter)

#     return cn
