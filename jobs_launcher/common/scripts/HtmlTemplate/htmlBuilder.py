# -*- coding: utf-8 -*-
from jinja2 import Environment
from jinja2 import PackageLoader
import argparse
import os
import json
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir, os.path.pardir)))
import core.config


def main():
    args = argparse.ArgumentParser()
    args.add_argument('--work_dir')

    args = args.parse_args()

    rendered_json = []
    notRenderedJson = {}
    compared = False
    try:
        with open(os.path.join(args.work_dir, core.config.TEST_REPORT_NAME_COMPARED), 'r') as file:
            rendered_json = json.loads(file.read())
    except Exception as err:
        core.config.main_logger.error(str(err))

    for img in rendered_json:
        if img['difference_color'] != "not compared yet":
            compared = True
            break

    env = Environment(
        loader=PackageLoader('htmlBuilder', 'templates'),
        autoescape=True
    )
    template = env.get_template('report.html')
    text = template.render(title="Render Results", compared=compared, rendered=rendered_json, not_rendered=notRenderedJson)

    with open(os.path.join(args.work_dir, 'result.html'), 'w') as f:
        f.write(text)


if __name__ == '__main__':
    main()
