function report = model_inventory(modelName, outFile)
%MODEL_INVENTORY Inspect an already loaded, stopped model without compiling.
% The caller owns loading/initialization in an isolated working-copy session.
% Masked, linked and referenced contents are deliberately not expanded.
% Output can contain private paths and parameter expressions. Review before sharing.
arguments
    modelName (1,1) string
    outFile (1,1) string = ""
end
if ~bdIsLoaded(modelName)
    error('CosimSkill:ModelNotLoaded', 'Load the intended working-copy model explicitly first.');
end
if ~strcmp(get_param(modelName, 'Type'), 'block_diagram')
    error('CosimSkill:NotRootModel', 'Pass a top-level model name, not a block path.');
end
if ~strcmp(get_param(modelName, 'SimulationStatus'), 'stopped')
    error('CosimSkill:ActiveModel', 'The helper does not inspect, stop or replace an active task.');
end
report.Schema = 'cosim-loaded-model-inventory/v1';
report.MATLAB = version;
report.Release = version('-release');
report.Platform = computer;
report.ModelName = char(modelName);
report.ModelFile = get_param(modelName, 'FileName');
report.Status = get_param(modelName, 'SimulationStatus');
report.Dirty = get_param(modelName, 'Dirty');
keys = {'SolverType', 'Solver', 'FixedStep', 'SimulationMode', 'StartTime', 'StopTime'};
for k = 1:numel(keys)
    report.Configuration.(keys{k}) = get_param(modelName, keys{k});
end
report.Coverage = struct('LoadedModelOnly', true, 'Compiled', false, ...
    'MaskedContentsExpanded', false, 'LibraryLinksFollowed', false, ...
    'ReferencedModelsExpanded', false, 'NativeExecution', 'UNVERIFIED');
report.TopLevelSubsystems = find_system(modelName, 'SearchDepth', 1, ...
    'LookUnderMasks', 'none', 'FollowLinks', 'off', 'BlockType', 'SubSystem');
blocks = find_system(modelName, 'LookUnderMasks', 'none', 'FollowLinks', 'off', ...
    'BlockType', 'S-Function');
report.SFunctions = struct('Block', {}, 'FunctionName', {}, 'ResolvedCandidates', {}, ...
    'ParameterExpression', {}, 'UncompiledPortCounts', {});
for k = 1:numel(blocks)
    name = get_param(blocks{k}, 'FunctionName');
    candidates = which(name, '-all');
    if isempty(candidates)
        candidates = {};
    elseif ischar(candidates)
        candidates = cellstr(candidates);
    end
    report.SFunctions(k) = struct('Block', blocks{k}, 'FunctionName', name, ...
        'ResolvedCandidates', {candidates}, ...
        'ParameterExpression', get_param(blocks{k}, 'Parameters'), ...
        'UncompiledPortCounts', get_param(blocks{k}, 'Ports'));
end
refs = find_system(modelName, 'LookUnderMasks', 'none', 'FollowLinks', 'off', ...
    'BlockType', 'ModelReference');
report.ModelReferences = struct('Block', {}, 'ModelName', {});
for k = 1:numel(refs)
    report.ModelReferences(k) = struct('Block', refs{k}, ...
        'ModelName', get_param(refs{k}, 'ModelName'));
end
report.Note = ['Port counts are not compiled vector widths. Function resolution is not proof ' ...
    'that a native solver executed. No parameter expression is evaluated by this helper.'];
if strlength(outFile) > 0
    if isfile(outFile) || isfolder(outFile)
        error('CosimSkill:OutputExists', 'Choose a new output file; existing evidence is preserved.');
    end
    folder = fileparts(outFile);
    if strlength(folder) > 0 && ~isfolder(folder)
        mkdir(folder);
    end
    [fid, message] = fopen(outFile, 'w', 'n', 'UTF-8');
    if fid < 0
        error('CosimSkill:WriteFailed', 'Could not write inventory: %s', message);
    end
    cleanup = onCleanup(@() fclose(fid)); %#ok<NASGU>
    fprintf(fid, '%s\n', jsonencode(report, PrettyPrint=true));
end
end
