import os
import argparse
import json
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir)))
import core.config


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--work_dir')
    args = argparser.parse_args()

    rendered_cases = set()
    expected_cases = set()
    common_info = {}

    try:
        with open(os.path.join(args.work_dir, core.config.TEST_REPORT_EXPECTED_NAME), 'r') as file:
            expected = json.loads(file.read())

        with open(os.path.join(args.work_dir, core.config.TEST_REPORT_NAME), 'r') as file:
            rendered = json.loads(file.read())

        rendered_cases = {x['test_case'] for x in rendered}
        expected_cases = {x for x in expected}
        common_info = {k: v for k, v in rendered[0].items() if k in core.config.RENDER_REPORT_BASE_USEFULL_KEYS}
    except OSError as err:
        core.config.main_logger.error("Not found report: {}".format(str(err)))
        return
    except (KeyError, IndexError) as err:
        core.config.main_logger.error("No one test was launched. Get empty report: {}".format(str(err)))

    skipped_cases = expected_cases - rendered_cases

    if skipped_cases:
        core.config.main_logger.error("Some tests were not launched")

        with open(os.path.join(args.work_dir, core.config.NOT_RENDERED_REPORT), 'w') as file:
            json.dump([x for x in skipped_cases], file, indent=4)

        for scase in skipped_cases:
            report_base = core.config.RENDER_REPORT_BASE.copy()
            report_base.update(
                {"test_case": scase,
                 "test_status": "error"}
            )
            report_base.update(common_info)
            rendered.append(report_base)

        with open(os.path.join(args.work_dir, core.config.TEST_REPORT_NAME), 'w') as file:
            json.dump(rendered, file, indent=4)
    else:
        core.config.main_logger.info("No missed tests detected")


if __name__ == '__main__':
    if not main():
        exit(0)
