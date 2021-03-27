from kubernetes import client, config
import argparse
import json


def create_snapshot(git_commit, pvc_name, snapshot_class_name, namespace="kubeflow"):
    # Loading k8s config for accesing APIs
    config.load_incluster_config()
    api = client.CustomObjectsApi()

    volume_snapshot_class_name = snapshot_class_name

    # Load names from pipeline config json file
    snapshot_name = "snapshot" + "-" + pvc_name + "-" + git_commit
    persistent_volume_claim_name = pvc_name

    # it's volume snapshot resource defined as Dict
    snapshot_resource = {
        "apiVersion": "snapshot.storage.k8s.io/v1beta1",
        "kind": "VolumeSnapshot",
        "metadata": {"name": snapshot_name},
        "spec": {
            "volumeSnapshotClassName": volume_snapshot_class_name,
            "source": {"persistentVolumeClaimName": persistent_volume_claim_name}
        }
    }

    # creating snapshot
    api.create_namespaced_custom_object(
        group="snapshot.storage.k8s.io",
        version="v1beta1",
        namespace=namespace,
        plural="volumesnapshots",
        body=snapshot_resource,
    )
    print("Snapshot created: ", snapshot_name)

    return snapshot_name


if __name__ == '__main__':
    # Using git_commit id passed by Jenkins at runtime with pipeline name to create unique pipeline version names linked with Jenkins build
    parser = argparse.ArgumentParser()
    parser.add_argument('--git_commit', required=True)
    args = parser.parse_args()

    # Load existing config to be updated
    with open('./config/pipeline.json') as pipeline_config:
        pipeline_config_data = json.load(pipeline_config)

    if bool(pipeline_config_data["pipeline_metadata"]["enable_snapshot"]):
        # create data snapshot
        data_snapshot_name = create_snapshot(git_commit=args.git_commit,
                                             pvc_name=pipeline_config_data["pipeline_run_params"]["data_pvc_name"] +"data",
                                             snapshot_class_name=pipeline_config_data["pipeline_metadata"][
                                                 "volume_snapshot_class_name"])

        model_snapshot_name = create_snapshot(git_commit=args.git_commit,
                                              pvc_name=pipeline_config_data["pipeline_run_params"]["model_pvc_name"] + "model",
                                              snapshot_class_name=pipeline_config_data["pipeline_metadata"][
                                                  "volume_snapshot_class_name"]
                                              )

        # update pipleine config with data snapshot name. Model snapshot is not used in the kubeflow pipeline, but can be used to restore in deployment mode with serving engine
        pipeline_config_data["pipeline_run_params"]["data_snapshot_name"] = data_snapshot_name
        with open('./config/pipeline.json', 'w+') as pipeline_config:
            json.dump(pipeline_config_data, pipeline_config)

        # set git_push flag
        # flag used as a check whether git push is needed or not. Saving it to file so it will be used later by Jenkins
        with open('git_push.txt', 'w+') as git_push:
            git_push.write("True")
    else:
        print("Snapshot is disabled!!!")
