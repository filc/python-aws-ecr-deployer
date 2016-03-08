import boto3
import yaml
from pprint import pprint

images = {'talent-pool': 23, 'l4c': 24}

client = boto3.client('s3')
s3_object = client.get_object(Bucket='lensa-staging-config', Key='scotty.yml')
config_text = s3_object['Body'].read()

config = yaml.load(config_text)

def get_image_name_from_docker_path(docker_path):
    if '/' in docker_path:
        return docker_path.split("/", 1)[1].split(':')[0]

    return ''

services = []
for service, info in config['services'].items():
    image_name = get_image_name_from_docker_path(info['containers'][0]['image_path'])
    if image_name in images:
        services.append((service, images[image_name]))

pprint(services)