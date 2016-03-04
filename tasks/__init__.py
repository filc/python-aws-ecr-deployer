from invoke import run, task


@task
def precommit(config=None):
    run('py.test --cov-config .coveragerc --cov-report term-missing --cov deployer tests/ --junit-xml pytests.xml')