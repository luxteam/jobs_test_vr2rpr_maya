set PATH=c:\python35\;c:\python35\scripts\;%PATH%
set FILE_FILTER=%1
set TESTS_FILTER="%2"

python ..\jobs_launcher\executeTests.py --test_filter %TESTS_FILTER% --file_filter %FILE_FILTER% --tests_root ..\jobs --work_root ..\Work\Results --work_dir vray2rpr --cmd_variables Tool "C:\Program Files\Autodesk\Maya2020\bin" ResPath "C:\TestResources\VRay2MayaAssets"