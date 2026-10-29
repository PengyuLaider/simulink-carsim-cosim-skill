function run_matlab_helper_test()
% Isolated structural helper test. No CarSim solver or real-vehicle claim.
root = fileparts(fileparts(mfilename('fullpath')));
scripts = fullfile(root, 'skills', 'simulink-carsim-cosim', 'scripts');
addpath(scripts);
pathCleanup = onCleanup(@() rmpath(scripts)); %#ok<NASGU>
[~, tag] = fileparts(tempname);
mdl = matlab.lang.makeValidName(['SkillInventory_' tag]);
assert(~bdIsLoaded(mdl), 'Test name already loaded; do not close it.');
new_system(mdl);
modelCleanup = onCleanup(@() close_system(mdl, 0)); %#ok<NASGU>
add_block('simulink/User-Defined Functions/S-Function', [mdl '/MissingNative'], ...
    'FunctionName', 'cosim_skill_missing_function_fixture');
add_block('simulink/Ports & Subsystems/Subsystem', [mdl '/Masked']);
Simulink.Mask.create([mdl '/Masked']);
add_block('simulink/User-Defined Functions/S-Function', [mdl '/Masked/HiddenFunction'], ...
    'FunctionName', 'cosim_skill_hidden_fixture');
dirtyBefore = get_param(mdl, 'Dirty');
report = model_inventory(mdl);
assert(strcmp(report.ModelName, mdl));
assert(strcmp(get_param(mdl, 'Dirty'), dirtyBefore));
assert(strcmp(get_param(mdl, 'SimulationStatus'), 'stopped'));
assert(~report.Coverage.Compiled);
assert(strcmp(report.Coverage.NativeExecution, 'UNVERIFIED'));
assert(~report.Coverage.MaskedContentsExpanded);
assert(numel(report.SFunctions) == 1, 'Masked content must remain unexpanded.');
assert(isempty(report.SFunctions(1).ResolvedCandidates));
assert(strcmp(report.SFunctions(1).FunctionName, 'cosim_skill_missing_function_fixture'));
try
    model_inventory('CosimSkillIntentionallyUnloadedFixture');
    error('Expected an unloaded-model error.');
catch errorInfo
    assert(strcmp(errorInfo.identifier, 'CosimSkill:ModelNotLoaded'));
end
output = string(tempname) + ".json";
outputCleanup = onCleanup(@() removeFixtureOutput(output)); %#ok<NASGU>
model_inventory(mdl, output);
loaded = jsondecode(fileread(output));
assert(~loaded.Coverage.Compiled);
raw = fileread(output);
try
    model_inventory(mdl, output);
    error('Expected an existing-output error.');
catch errorInfo
    assert(strcmp(errorInfo.identifier, 'CosimSkill:OutputExists'));
end
assert(strcmp(raw, fileread(output)));
fprintf('MATLAB_HELPER_TEST_PASS: inventory only, no compile or native solver execution.\n');
end

function removeFixtureOutput(path)
if isfile(path)
    delete(path);
end
end
