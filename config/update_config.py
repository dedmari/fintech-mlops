import json
import kfp
import ast
import os

# def update_pipeline_config(key_type, key, value):
#     """ Updating value of a key within kubeflow pipeline config file.
#
#     Args:
#         key_type (str): keytype can be "pipeline_run_params" or "pipeline_metadata"
#         key (str): key identifying the config
#         value (str): new value of the key
#
#     """
#     # Considering script is executed from parent directory
#
#     # Load existing config to be updated
#     with open('./config/pipeline.json') as pipeline_config:
#         data = json.load(pipeline_config)
#         pipeline_keytype_params = data[key_type]
#
#     # check if value needs to be updated and set git_push flag accordingly
#     if pipeline_keytype_params[key] != value:
#         # Updating value of the key
#         pipeline_keytype_params[key] = value
#         data[key_type] = pipeline_keytype_params
#
#     # Updating config file with new value
#     with open('./config/pipeline.json', 'w+') as pipeline_config:
#         json.dump(data, pipeline_config)


if __name__ == '__main__':

    # current kfp run id
    with open('recent_run_id.txt') as run:
        run_id = run.read()

    # Load existing config to be updated
    with open('./config/pipeline.json') as pipeline_config:
        pipeline_config_data = json.load(pipeline_config)

    kfp_client = kfp.Client()
    run_info_dict = kfp_client.runs.get_run(run_id).to_dict()

    print("run id: ", run_id)

    print("-----------------------------------")

    print(run_info_dict)

    # kubeflow pipeline run always prepends workflow name with volume name.
    # content within 'workflow_manifest' key is string. Using ast.literal_eval to convert it to dict and return run's workflow name
    run_workflow_name = ast.literal_eval(run_info_dict['pipeline_runtime']['workflow_manifest'])['metadata']['name']

    config_updated = False
    # data PVC name update
    if (pipeline_config_data["pipeline_run_params"]["download_data"] == "True") or (
            pipeline_config_data["pipeline_run_params"]["restore_data_from_snasphot"] == "True"):

        # get kubeflow_run workspace name and prepend to data_pvc_name
        existing_pvc_name = pipeline_config_data["pipeline_run_params"]["data_pvc_name"]

        # Append run_workflow_name with "-"+volume_name passed as runtime parameter (Kubeflow pipeline style)
        new_pvc_name = run_workflow_name + "-" + existing_pvc_name
        pipeline_config_data["pipeline_run_params"]["data_pvc_name"] = new_pvc_name

        config_updated = True

    # model PVC name update
    if pipeline_config_data["pipeline_run_params"]["use_existing_model_pvc"] == "False":

        # get kubeflow_run workspace name and prepend to model_pvc_name
        existing_pvc_name = pipeline_config_data["pipeline_run_params"]["model_pvc_name"]

        # Append run_workflow_name with "-"+volume_name passed as runtime parameter (Kubeflow pipeline style)
        new_pvc_name = run_workflow_name + "-" + existing_pvc_name
        pipeline_config_data["pipeline_run_params"]["model_pvc_name"] = new_pvc_name

        config_updated = True

    # Updating config file with new values
    if config_updated:
        with open('./config/pipeline.json', 'w+') as pipeline_config:
            json.dump(pipeline_config_data, pipeline_config)

    # flag used as a check whether git push is needed or not. Saving it to file so it will be used later by Jenkins
    with open('git_push.txt', 'w') as git_push:
        git_push.write(str(config_updated))

    # delete file consisting current run_id
    os.remove('recent_run_id.txt')
