import os
import maya.cmds as cmds
import maya.mel as mel
import convertRS2RPR
import datetime
import json


def rpr_render(scene):

	cmds.optionVar(rm="RPR_DevicesSelected")
	cmds.optionVar(iva=("RPR_DevicesSelected", 1))

	scenes_cam_fix_1 = [ "LightEnv.ma", "LightEnv1.ma", "LightEnv2.ma", "LightEnv3.ma", "LightDome1.ma", "LightDome2.ma", "LightDome3.ma", "LightDome4.ma", "LightDome5.ma", "LightDome6.ma", "LightDome7.ma",
		"IES1.ma", "IES2.ma", "IES3.ma", "IES4.ma", "IES5.ma", "IES6.ma",
		"PhysicalSky1.ma", "PhysicalSky2.ma", "PhysicalSky3.ma", "PhysicalSky4.ma", "PhysicalSky5.ma", "PhysicalSky6.ma", "PhysicalSky7.ma",
		"Triplanar.ma", "Triplanar1.ma", "Triplanar2.ma", "Triplanar3.ma", "Triplanar4.ma", "Triplanar5.ma", "Triplanar6.ma", "Triplanar7.ma", "Triplanar8.ma", "Triplanar9.ma",
		"Architectural1.ma", "Architectural10.ma", "Architectural11.ma", "Architectural12.ma", "Architectural2.ma", "Architectural3.ma", "Architectural4.ma", "Architectural5.ma", "Architectural6.ma", "Architectural7.ma", "Architectural8.ma", "Architectural9.ma",
		"rsMaterial.ma", "rsMaterial1.ma", "rsMaterial10.ma", "rsMaterial11.ma", "rsMaterial12.ma", "rsMaterial13.ma", "rsMaterial14.ma", "rsMaterial15.ma", "rsMaterial16.ma", "rsMaterial17.ma", "rsMaterial18.ma", "rsMaterial19.ma", "rsMaterial2.ma", "rsMaterial20.ma", "rsMaterial21.ma", "rsMaterial22.ma", "rsMaterial23.ma", "rsMaterial24.ma", "rsMaterial25.ma", "rsMaterial26.ma", "rsMaterial27.ma", "rsMaterial28.ma", "rsMaterial29.ma", "rsMaterial3.ma", "rsMaterial30.ma", "rsMaterial31.ma", "rsMaterial32.ma", "rsMaterial33.ma", "rsMaterial34.ma", "rsMaterial35.ma", "rsMaterial36.ma", "rsMaterial37.ma", "rsMaterial38.ma", "rsMaterial39.ma", "rsMaterial4.ma", "rsMaterial40.ma", "rsMaterial41.ma", "rsMaterial42.ma", "rsMaterial43.ma", "rsMaterial44.ma", "rsMaterial5.ma", "rsMaterial6.ma", "rsMaterial7.ma", "rsMaterial8.ma", "rsMaterial9.ma",
		"LightArea.ma", "LightArea1.ma", "LightArea10.ma", "LightArea11.ma", "LightArea12.ma", "LightArea2.ma", "LightArea3.ma", "LightArea4.ma", "LightArea5.ma", "LightArea6.ma", "LightArea7.ma", "LightArea8.ma", "LightArea9.ma", "LightAreaCylinder.ma", "LightAreaDisk.ma", "LightAreaMesh.ma", "LightAreaRectangle.ma", "LightAreaSize100.ma", "LightAreaSize50.ma", "LightAreaSize50x25.ma", "LightAreaSphere.ma",
		"LightPhysDirect.ma", "LightPhysDirect1.ma", "LightPhysDirect2.ma", "LightPhysDirect3.ma", "LightPhysDirect4.ma", "LightPhysDirect5.ma",
		"LightPoint.ma", "LightPoint1.ma", "LightPoint10.ma", "LightPoint2.ma", "LightPoint3.ma", "LightPoint4.ma", "LightPoint5.ma", "LightPoint6.ma", "LightPoint7.ma", "LightPoint8.ma", "LightPoint9.ma",
		"SpotLight.ma", "SpotLight1.ma", "SpotLight10.ma", "SpotLight11.ma", "SpotLight2.ma", "SpotLight3.ma", "SpotLight4.ma", "SpotLight5.ma", "SpotLight6.ma", "SpotLight7.ma", "SpotLight8.ma", "SpotLight9.ma" ]
	
	scenes_cam_fix_2 = [ "VolumeScattering.ma", "VolumeScattering1.ma", "VolumeScattering2.ma", "VolumeScattering3.ma", "VolumeScattering4.ma", "VolumeScattering5.ma", "VolumeScattering6.ma", "VolumeScattering7.ma", "VolumeScattering8.ma", "VolumeScattering9.ma",
		"LightPortal.ma", "LightPortal1.ma", "LightPortal2.ma", "LightPortal3.ma", "LightPortal4.ma", "LightPortal5.ma" ]
	
	cameras = cmds.ls(cameras=True)
	if ("cameraShape1" in cameras):
		mel.eval("lookThru camera1")
		'''
        for each in scenes_cam_fix_1: 
			if each == scene:
				try:
					cmds.setAttr("cameraShape1.focalLength", 52.3)
				except:
					print "[ERROR]: Can't set focalLength\n";
		for each in scenes_cam_fix_2:
			if each == scene:
				try:
					cmds.setAttr("cameraShape1.focalLength", 36)
				except:
					print "[ERROR]: Can't set focalLength\n";
        '''
	else:
		print "[ERROR]: no camera1\n";
	
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

	if not cmds.pluginInfo("redshift4maya", q=True, loaded=True):
		cmds.loadPlugin("redshift4maya")

	if not cmds.pluginInfo("RadeonProRender", q=True, loaded=True):
		cmds.loadPlugin("RadeonProRender")

	convertRS2RPR.auto_launch()

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
	report['difference_color'] = "not compared yet"
	report['test_status'] = "passed"
	report['difference_time'] = "not compared yet"
	report['difference_time_or'] = "not compared yet"

	with open(filePath, 'w') as file:
		json.dump([report], file, indent=4)


def main():

	mel.eval("setProject(\"{res_path}\")")
	tests = {tests}
	for each in tests:
		prerender(each, 300)
	cmds.evalDeferred(cmds.quit(abort=True))
