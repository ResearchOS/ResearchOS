% Load this from the config file.

mfilepath = mfilename("fullpath");
matlab_folder_in_pkg = fileparts(mfilepath);
pkg_folder = fileparts(matlab_folder_in_pkg);
config_path = [pkg_folder filesep 'config' filesep 'config.json'];

% process_run_file_path = base_path + filesep + "proecss_run.mat";

% Check if the process_run file exists.
str = fileread(config_path);
config = jsondecode(str);
if config.process_run_tmp_folder == "."
    folder_path = pkg_folder;
else
    folder_path = config.process_run_tmp_folder;
end
process_run_file_path = [folder_path, filesep, config.process_run_file_name]; 

while true

    if ~exist(process_run_file_path, "file")
        pause(1); % Wait for 1 second before checking again.
        continue;
    end

    process_run_folder = fileparts(process_run_file_path);

    % Load the process_run file from the disk.
    load(process_run_file_path, "process_run_var");

    % Get the mfolder path.
    mfolder_path = process_run_var.mfolder;
    addpath(genpath(mfolder_path));

    % Get the function name.
    mfunc_name = process_run_var.mfunc_name;
    fcn_handle = str2func(mfunc_name);
   
    % Get the input & output arguments. They are structs with fieldnames set to the variable order number. 
    % Within each number is a struct with fields "name_in_code", "vr_id", and "value".

    % This is a struct where the fieldnames are the variable ID's, and they have fields "name_in_code" and "value".
    input_vrs = process_run_var.input_vrs;
    % This is a struct where the fieldnames are the variable names in code, and they have fields "var_id" and "value".
    output_vrs = process_run_var.output_vrs;

    n_inputs = length(fieldnames(input_vrs));
    n_outputs = length(fieldnames(output_vrs));

    vr_values_in = cell(1, n_inputs);
    for i = 1:n_inputs
        fldName = num2str(i);
        vr_values_in{i} = input_vrs.(['a', fldName]).value;
    end

    % process_run the command
    outputs_char = '[';
    output_vr_names = cell(1,n_outputs);
    for i = 1:n_outputs
        fldName = ['a' num2str(i)];
        output_vr_names{i} = output_vrs.(fldName).name_in_code;
        outputs_char = [outputs_char, output_vr_names{i} ', '];
    end
    outputs_char = [outputs_char(1:end-2), ']'];
    eval([outputs_char ' = feval(fcn_handle, vr_values_in{:});']);

    % Get the output arguments.    
    for i = 1:n_outputs
        fldName = num2str(i);
        output_vrs.(['a', fldName]).value = jsonencode(eval(output_vr_names{i}));
    end

    process_run_var.output_vrs = output_vrs;

    results_process_run_file_path_tmp = [process_run_folder filesep 'tmp_process_run_results.mat'];
    save(results_process_run_file_path_tmp, 'process_run_var','-v6');

    % Delete the process_run file.
    delete(process_run_file_path);

    % Remove the folder from the path.
    rmpath(genpath(mfolder_path));

    % Rename the output file to remove the tmp_ prefix.
    results_process_run_file_path = [process_run_folder filesep 'process_run_results.mat'];
    movefile(results_process_run_file_path_tmp, results_process_run_file_path);

end