import kfp
import json

kubeflow_host = ''
with open('./config/kubeflow.json') as kf_config:
    data = json.load(kf_config)
    kubeflow_host = data['kubeflow'][0]['host']

pipeline_run_params = {}
pipeline_metadata = {}
with open('./config/pipeline.json') as pipeline_config:
    data = json.load(pipeline_config)
    pipeline_run_params = data['pipeline_run_params']
    pipeline_metadata = data['pipeline_metadata']

pipeline_id = pipeline_metadata['pipeline_id']
run_name = pipeline_metadata['pipeline_run_name']
pipeline_version_id = pipeline_metadata['pipeline_version_id']

client = kfp.Client()

if pipeline_metadata['use_existing_experiment'] == "False":
    # Create a new experiment
    exp_resp = client.create_experiment(pipeline_metadata['experiment_name'])
    experiment_id = exp_resp.to_dict()['id']
else:
    # Retrieve id of an existing experiment
    experiment_id = client.get_experiment(experiment_name=pipeline_metadata['experiment_name']).to_dict()['id']

if pipeline_metadata['use_existing_pipeline'] == "True":
    run = client.run_pipeline(experiment_id=experiment_id, version_id=pipeline_version_id,
                              job_name=run_name,
                              params=pipeline_run_params)
else:
    run = client.run_pipeline(experiment_id=experiment_id, pipeline_id=pipeline_id, job_name=run_name,
                              params=pipeline_run_params)
print('Run link: %s%s/#/runs/details/%s' % (kubeflow_host, client._get_url_prefix(), run.id))

with open('recent_run_id.txt', 'w') as run_id:
    run_id.write(run.id)
