from kubernetes import client, config

def main():
    config.load_incluster_config()

    api = client.CustomObjectsApi()

    volume_snapshot_class_name = "netapp-snapclass"

    # Load names from pipeline config json file
    snapshot_name = "test-jenkins-client-snapshot"
    persistent_volume_claim_name = "stock-time-series-forecast-2hm6p-djia-time-series-model"
    namespace = "kubeflow"

    # it's volume snapshot resource defined as Dict
    snapshot_resource = {
        "apiVersion": "snapshot.storage.k8s.io/v1beta1",
        "kind": "VolumeSnapshot",
        "metadata": {"name": snapshot_name},
        "spec": {
            "volumeSnapshotClassName": volume_snapshot_class_name,
            "source": { "persistentVolumeClaimName": persistent_volume_claim_name}
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
    print("Snapshot created")


if __name__ == '__main__':
    main()