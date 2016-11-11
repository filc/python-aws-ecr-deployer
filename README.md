[![Build Status](https://travis-ci.org/filc/python-aws-ecr-deployer.svg?branch=master)](https://travis-ci.org/filc/python-aws-ecr-deployer)

#AWS ECR-ECS deployer

## Installation / running

To run the application, the aws credentials are needed to be set somehow. In local environment it can be done with [this way](http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html). If it's run with docker, the aws environment variable must be set except for it's running on aws instances with the appropriate security settings.

### Local / development

Create a virtualenv and activate it (pyvenv .ve && . .ve/bin/activate)

```
pip3 install -r requirements.txt
```

Make sure the tests are succefully run

```
inv precommit
```

Run with dev config and debug mode

```
python3 serve.py -d -c config/dev.py
```

Run with production config (it will communicate with the aws services)

```
python3 serve.py
```

### Production environment / run with docker

```
docker build -t deployer .

docker run -ti --rm -p 5000:7000 -e DP_ECR_REGISTRY=0123456789 deployer inv precommit

docker run -ti --rm -p 5000:7000 -e DP_ECR_REGISTRY=0123456789 -e DP_ECR_REGION=us-east-1 -e DP_ECS_REGION=us-east-1 deployer

```

## Environment variables

* DP_BASE_URL (optional) - base url of the application like "http://example.com/deployer"
* DP_APP_ROOT (optional) - root dir of the application
* DP_ECS_CLUSTER (required) - name of the ecs cluster
* DP_ECR_REGISTRY (required) - id of the ecr registry
* DP_ECR_REGION (optional)
* DP_ECS_REGION (optional)
* DP_S3_REGION (optional)
* DP_SCOTTY_YML_S3_BUCKET (required) - bucket of the scotty config yaml file
* DP_SCOTTY_YML_S3_KEY (required) - key of the scotty config yaml file (filename)

### AWS specified environment variables

* AWS_ACCESS_KEY_ID - The access key for your AWS account.
* AWS_SECRET_ACCESS_KEY - The secret key for your AWS account.
* AWS_DEFAULT_REGION - The default region to use, e.g. us-east-1.
* AWS_PROFILE - The default credential and configuration profile to use, if any.

# Further tasks

* Error handling
* Controller tests (integration tests)
* Check repo version on deploy (don't deploy images with version 0)
* Handle more clusters
