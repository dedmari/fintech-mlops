import json


def update_pipeline_config(key_type, key, value):
    """ Updating value of a key within kubeflow pipeline config file.

    Args:
        key_type (str): keytype can be "pipeline_run_params" or "pipeline_metadata"
        key (str): key identifying the config
        value (str): new value of the key

    """
    # Considering script is executed from parent directory

    # Load existing config to be updated
    with open('./config/pipeline.json') as pipeline_config:
        data = json.load(pipeline_config)
        pipeline_keytype_params = data[key_type]

    # Updating value of the key
    pipeline_keytype_params[key] = value
    data[key_type] = pipeline_keytype_params

    # Updating config file with new value
    with open('./config/pipeline.json', 'w+') as pipeline_config:
        json.dump(data, pipeline_config)


if __name__ == '__main__':
    update_pipeline_config("pipeline_metadata", "pipeline_run_name", "Snapshot: Fintech Jenkins triggered run")