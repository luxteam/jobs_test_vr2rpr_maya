import os
import maya.cmds as cmds
import maya.mel as mel
import convertVR2RPR
import datetime
import json


def rpr_render(scene):

	cmds.optionVar(rm="RPR_DevicesSelected")
	cmds.optionVar(iva=("RPR_DevicesSelected", 1))
	
	cmds.fireRender(waitForItTwo=True)

	start_time = datetime.datetime.now()
	mel.eval("renderIntoNewWindow render")
	output = os.path.join("{work_dir}", "Color", "converted_" + scene)
	cmds.renderWindowEditor("renderView", edit=True, dst="color")
	cmds.renderWindowEditor("renderView", edit=True, com=True, writeImage=output)
	end_time = datetime.datetime.now()

	return (end_time - start_time).total_seconds()


def prerender(scene, rpr_iter):

	scene_name  = cmds.file(q=True, sn=True, shn=True)
	print ("Processing: " + scene_name + "\n");
	if scene_name != scene:
		try:
			cmds.file(scene, f=True, options="v=0;", ignoreVersion=True, o=True)
		except:
			print("Failed to open scene")
			cmds.evalDeferred(cmds.quit(abort=True))

	if not cmds.pluginInfo("vrayformaya", q=True, loaded=True):
		cmds.loadPlugin("vrayformaya")

	if not cmds.pluginInfo("RadeonProRender", q=True, loaded=True):
		cmds.loadPlugin("RadeonProRender")

	convertVR2RPR.auto_launch()

	print "Conversion finished.\n";

	cmds.setAttr("defaultRenderGlobals.currentRenderer", "FireRender", type="string")
	cmds.setAttr("defaultRenderGlobals.imageFormat", 8)
	cmds.setAttr("RadeonProRenderGlobals.completionCriteriaIterations", rpr_iter)

	render_time = rpr_render(scene)

	print "Render finished. Render time: {{}}\n".format(render_time);

	filePath = "{work_dir}" + "/" + scene + "_RPR.json"
	report = {{}}
	report['render_device'] = cmds.optionVar(q="RPR_DevicesName")[0]
	report['tool'] = "Maya " + cmds.about(version=True)
	report['date_time'] = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
	report['render_version'] = mel.eval("getRPRPluginVersion()")
	report['core_version'] = mel.eval("getRprCoreVersion()")
	report['file_name'] = "converted_" + scene + ".jpg"
	report['render_color_path'] = "Color/converted_" + scene + ".jpg"
	report['baseline_color_path'] = "Color/" + scene + ".jpg"
	report['scene_name'] = scene
	report['render_time'] = render_time
	report['test_case'] = scene
	report['difference_color'] = -0
	report['test_status'] = "passed"
	report['difference_time'] = -0
	report['difference_time_or'] = -0

	with open(filePath, 'w') as file:
		json.dump([report], file, indent=4)


def main():
	mel.eval("setProject(\"{res_path}\")")
	tests = {tests}
	for each in tests:
		prerender(each, 300)
	cmds.evalDeferred("cmds.quit(abort=True)")
