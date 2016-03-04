
# -*- coding: utf-8 -*-

import argparse
import os
from deployer import create_app
from filcutils.configs import load_configs

current_dir = os.path.dirname(os.path.realpath(__file__))
configs = ['{}/config/application.py'.format(current_dir)]


def get_args():
    parser = argparse.ArgumentParser(description='ats')
    parser.add_argument('-c', '--config', type=str, required=False)
    parser.add_argument('-d', '--debug', dest='debug', action='store_true')
    parser.add_argument('-p', '--port', type=int, required=False)
    parser.set_defaults(feature=True)
    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()

    if args.config:
        configs.append('{}/{}'.format(current_dir, args.config))

    config = load_configs(configs)
    app = create_app(config)
    app.run(host='0.0.0.0', debug=args.debug or False, port=args.port or 5000, use_reloader=True)
else:
    config = load_configs(configs)
    app = create_app(config)
    app.debug = True
