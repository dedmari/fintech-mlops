from kubernetes import config, client
from kubernetes.client.api import core_v1_api
from kubernetes.client import V1DeleteOptions
import json


def update_model_config(model_pvc_name="fintech-model-pvc", model_version=3,
                        namespace="kubeflow", tf_serve_name='fintech', base_path='/mnt'):
    create_model_config_cmd = 'mkdir -p /mnt/model_config && echo "model_config_list {\\n  config {\\n    name: \'' + tf_serve_name + '\'\\n    base_path: \'' + base_path + '\'\\n    model_platform: \'tensorflow\'\\n    model_version_policy {\\n       specific {\\n        versions: ' + str(
        model_version) + '\\n      }\\n    }\\n  }\\n}" > cat > /mnt/model_config/models.config'
    config.load_incluster_config()
    core_v1 = core_v1_api.CoreV1Api()
    # print("Creating Pod for updating model.config")
    pod_manifest = {
        'apiVersion': 'v1',
        'kind': 'Pod',
        'metadata': {
            'name': 'update-model-config'
        },
        'spec': {
            'containers': [{
                'image': 'ubuntu:18.04',
                'name': 'ubuntu',
                "args": [
                    "/bin/sh",
                    "-c",
                    create_model_config_cmd
                ],
                'volumeMounts': [{
                    'mountPath': "/mnt",
                    'name': 'model-pvc'
                }]
            }],
            'volumes': [{
                'name': 'model-pvc',
                'persistentVolumeClaim': {'claimName': model_pvc_name}
            }],
            'restartPolicy': 'Never'
        }
    }
    resp = core_v1.create_namespaced_pod(body=pod_manifest, namespace=namespace)
    while True:
        resp = core_v1.read_namespaced_pod(name='update-model-config',
                                           namespace='kubeflow')
        if resp.status.phase != 'Pending':
            break

    # delete pod
    core_v1.delete_namespaced_pod(name='update-model-config',
                                  namespace=namespace,
                                  body=V1DeleteOptions(),
                                  grace_period_seconds=0,
                                  propagation_policy="Background")


def deploy_model(model_pvc="fintech-model-pvc", tf_serve_deploy_name="fintech-v1", namespace="kubeflow",
                 label_selector="app=fintech"):
    config.load_incluster_config()
    apps_api = client.AppsV1Api()
    resp = apps_api.read_namespaced_deployment(name=tf_serve_deploy_name, namespace=namespace)
    existing_model_pvc = resp.spec.template.spec.volumes[0].persistent_volume_claim.claim_name

    if model_pvc != existing_model_pvc:
        # update claim name
        resp.spec.template.spec.volumes[0].persistent_volume_claim.claim_name = model_pvc

        # update the deployment
        api_response = apps_api.patch_namespaced_deployment(
            name=tf_serve_deploy_name,
            namespace=namespace,
            body=resp)
    else:
        # if deployment not patched, pod/s needs to be re-deployed in order to load new model.config file (deleting pod)
        # Delete pods
        v1 = client.api.CoreV1Api()
        selected_label_pods = v1.list_namespaced_pod(namespace=namespace, label_selector=label_selector)
        body = client.V1DeleteOptions()
        for pod in selected_label_pods.items:
            v1.delete_namespaced_pod(pod.metadata.name, namespace=namespace, body=body)


if __name__ == '__main__':
    # load existing config to be updated
    with open('./config/pipeline.json') as pipeline_config:
        pipeline_config_data = json.load(pipeline_config)

    namespace = "kubeflow"
    model_pvc_name = pipeline_config_data["pipeline_run_params"]["model_pvc_name"]
    model_version = pipeline_config_data["pipeline_run_params"]["model_tag"]
    tf_serve_name = pipeline_config_data["model_serve"]["tf_serve_name"]
    base_path = pipeline_config_data["model_serve"]["base_path"]
    tf_serve_deploy_name = pipeline_config_data["model_serve"]["tf_serve_deploy_name"]
    label_selector = pipeline_config_data["model_serve"]["label_selector"]

    update_model_config(model_pvc_name=model_pvc_name, model_version=model_version,
                        namespace=namespace, tf_serve_name=tf_serve_name, base_path=base_path)

    deploy_model(model_pvc=model_pvc_name, tf_serve_deploy_name=tf_serve_deploy_name, namespace=namespace,
                 label_selector=label_selector)
