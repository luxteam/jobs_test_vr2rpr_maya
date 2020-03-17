import argparse
import sys
import os
import subprocess
import psutil
import json
import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir)))
from jobs_launcher.core.config import main_logger
from jobs_launcher.core.config import RENDER_REPORT_BASE


def createArgsParser():
    parser = argparse.ArgumentParser()

    parser.add_argument('--tests_list', required=True, metavar="<path>")
    parser.add_argument('--render_path', required=True, metavar="<path>")
    parser.add_argument('--scene_path', required=True, metavar="<path")
    parser.add_argument('--output_dir', required=True)
    parser.add_argument('--output_img_dir', required=True)
    parser.add_argument('--output_file_ext', required=True)
    return parser


def get_or_render_time(log_name):
    with open(log_name, 'r') as file:
        for line in file.readlines():
            if "[Vray] Rendering done - total time for 1 frames:" in line:
                time_s = line.split(": ")[-1]

                try:
                    x = datetime.datetime.strptime(time_s.replace('\n', '').replace('\r', ''), '%S.%fs')
                except ValueError:
                    x = datetime.datetime.strptime(time_s.replace('\n', '').replace('\r', ''), '%Mm:%Ss')
                # 	TODO: proceed H:M:S

                return float(x.second + x.minute * 60 + float(x.microsecond / 1000000))


def main():
    args = createArgsParser().parse_args()

    tests_list = {}
    with open(args.tests_list, 'r') as file:
        tests_list = json.loads(file.read())

    try:
        os.makedirs(args.output_img_dir)
    except OSError as err:
        main_logger.error(str(err))
        return 1

    for test in tests_list:
        scene = test['name']
        try:
            scenePath = os.path.join(args.scene_path)
            try:
                temp = os.path.join(scenePath, scene[:-3])
                if os.path.isdir(temp):
                    scenePath = temp
            except:
                pass
            scenePath = os.path.join(scenePath, scene)
            with open(scenePath) as f:
                scene_file = f.read()
            license = 'fileInfo "license" "student";'
            scene_file = scene_file.replace(license, '')
            scene_file = scene_file.replace('setAttr ".pmt" 0;', 'setAttr ".pmt" 0.5;')
            with open(scenePath, 'w') as f:
                f.write(scene_file)
        except:
            pass

        if test['status'] == 'active':
            case_report = RENDER_REPORT_BASE
            case_report.update({
                "original_color_path": "Color/" + test['name'] + '.' + args.output_file_ext,
                "original_render_log": test['name'] + '.or.log'
            })
            render_log_path = os.path.join(args.output_dir, test['name'] + '.or.log')

            scenes_without_camera1 = ['Bump', 'BumpBlender', 'Displacement', 'DisplacementBlender', 'Fresnel', 'Normal',
                                      'CarPaint', 'Incandescent', 'SubsurfaceScatter', 'AmbientOcclusion', 'CameraMap',
                                      'Noise', 'ColorLayer']
            use_camera1 = " -cam Camera001"
            if os.path.basename(args.output_dir) in scenes_without_camera1:
                use_camera1 = ""
            cmd_script = '"{}" -r vray -proj "{}" -log {} -rd "{}" -im "{}" -of {}{} "{}"' \
                .format(args.render_path, args.scene_path, render_log_path, args.output_img_dir,
                        os.path.join(args.output_img_dir, test['name']), args.output_file_ext, use_camera1,
                        os.path.join(args.scene_path, test['name']))
            cmd_script_path = os.path.join(args.output_dir, test['name'] + '.vray.bat')

            try:
                with open(cmd_script_path, 'w') as file:
                    file.write(cmd_script)
                with open(render_log_path, 'w') as file:
                    pass
            except OSError as err:
                main_logger.error("Error while saving bat: {}".format(str(err)))
            else:
                rc = -1
                os.chdir(args.output_dir)
                p = psutil.Popen(cmd_script_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = p.communicate()

                try:
                    rc = p.wait()
                except psutil.TimeoutExpired as err:
                    main_logger.error("Terminated by simple render. {}".format(str(err)))
                    rc = -1
                    for child in reversed(p.children(recursive=True)):
                        child.terminate()
                    p.terminate()
                # return rc
                if rc == 0:
                    case_report['render_time'] = get_or_render_time(case_report['original_render_log'])
                    with open(os.path.join(args.output_dir, test['name'] + '_Vray.json'), 'w') as file:
                        json.dump([case_report], file, indent=4)
    return 0


if __name__ == "__main__":
    exit(main())
