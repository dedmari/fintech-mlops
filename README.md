<div align="center">
<h1>MLOps for Production Grade Machine Learning</h1>
<h2> MLOps: Fintech use-case </h2>
</div>
This repository contains the implementation of MLOps setup discussed in articles:

 - [Demystifying MLOps : Part 1](https://blog.netapp.com/demystifying-mlops-part-1+)🚀
 - [Demystifying MLOps : Part 2](https://community.netapp.com/t5/Tech-ONTAP-Blogs/Demystifying-MLOps-Part-2/ba-p/167865)🚀

## Prerequisite
- [Kubernetes v1.18](https://v1-18.docs.kubernetes.io/docs/setup/) or above

## Install Trident (dynamic storage orchestrator) using helm
Install helm, if not already available:

    curl https://baltocdn.com/helm/signing.asc | sudo apt-key add -  
    sudo apt-get install apt-transport-https --yes
    echo "deb https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
    sudo apt-get update
    sudo apt-get install helm
Download and extract Trident 20.01.1 installer:

    $wget https://github.com/NetApp/trident/releases/download/v21.01.1/trident-installer-21.01.1.tar.gz
    $tar -xf trident-installer-21.01.1.tar.gz
    $cd trident-installer/helm
    
  Install trident with Helm:
 
    $helm install trident trident-operator-21.01.0.tgz --namespace trident --create-namespace
  Creating a Trident backend:
  <br>
  You can now go ahead and create a backend that will be used by Trident to provision volumes. To do this, create a  `backend.json`  file that contains the necessary parameters. Sample configuration files for different backend types can be found in the  `sample-input`  directory of `trident-installer`.

Visit the  [backend configuration guide](https://netapp-trident.readthedocs.io/en/stable-v21.01/kubernetes/operations/tasks/backends/index.html#backend-configuration)  for more details about how to craft the configuration file for your backend type.

    cp sample-input/<backend template>.json backend.json
    # Edit backend.json and fill out the template for your backend
    vi backend.json
    ./tridentctl -n trident create backend -f backend.json

## Create a storage class for Trident
This storage class will be used to create Persistent Volume Claims (PVCs) and store persistent data.
Lets use the underneath yaml fie to create storage class.
The simplest storage class to start with is one based on the `trident-installer/sample-input/storage-class-csi.yaml.templ` file that comes with the installer, replacing `__BACKEND_TYPE__` with the storage driver name.

    kubectl create -f sample-input/storage-class-basic-csi.yaml
 Kubeflow installation requires a default storage class. We can patch the storage class created above (if not already set to default):
 
    kubectl patch storageclass basic-csi -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'

## Install Kubeflow v1.0
Visit [https://v1-0-branch.kubeflow.org/docs/started/k8s/kfctl-k8s-istio/](https://v1-0-branch.kubeflow.org/docs/started/k8s/kfctl-k8s-istio/) and follow the installation instructions 

## Deploy and set up volume snapshot components on K8s
If your cluster does not come pre-installed with the correct volume-snapshot components, you may manually install these components by executing the following steps:

 - Install Snapshot Beta CRDs:
 
       kubectl create -f https://raw.githubusercontent.com/kubernetes-csi/external-snapshotter/release-3.0/client/config/crd/snapshot.storage.k8s.io_volumesnapshotclasses.yaml
       kubectl create -f https://raw.githubusercontent.com/kubernetes-csi/external-snapshotter/release-3.0/client/config/crd/snapshot.storage.k8s.io_volumesnapshotcontents.yaml
       kubectl create -f https://raw.githubusercontent.com/kubernetes-csi/external-snapshotter/release-3.0/client/config/crd/snapshot.storage.k8s.io_volumesnapshots.yaml
 - Install Snapshot Controller:
   
        kubectl apply -f https://raw.githubusercontent.com/kubernetes-csi/external-snapshotter/release-3.0/deploy/kubernetes/snapshot-controller/rbac-snapshot-controller.yaml
        kubectl apply -f https://raw.githubusercontent.com/kubernetes-csi/external-snapshotter/release-3.0/deploy/kubernetes/snapshot-controller/setup-snapshot-controller.yaml
        
## Setup K8s VolumeSnapshotClass
 For creating a Volume Snapshot, a [VolumeSnapshotClass](https://netapp-trident.readthedocs.io/en/stable-v20.01/kubernetes/concepts/objects.html#kubernetes-volumesnapshotclass-objects) must be set up. We will create a volume snapshot class and it will be used to achieve ML versioning by leveraging NetApp Snapshot technology.
 
 - In this repository, you will find a folder `netapp-snaphot-class-config` having a VolumeSnapshotClass yaml file, namely `netapp-volume-snapshot-class.yaml`. Let's create VolumeSnapshotClass  `netapp-csi-snapclass`  and set it to default VolumeSnapshotClass:
 
       kubectl create -f netapp-snaphot-class-config/netapp-volume-snapshot-class.yaml

## Install Jenkins with required plugins
We are using Jenkins for CI/CD. Go to folder `jenkins-k8s` to find relevant files for deploying Jenkins. To install Jenkins on the same Kubernetes (K8s) cluster as that of Kubeflow, follow the steps mentioned underneath:

 - Create K8s namespace for Jenkins:
 
	   kubectl create namespace jenkins
- Create Persistent Volume Claim for Jenkins. It will be used to store Jenkins application data. Trident is going to dynamically allocate Persistent Volume. 

      kubectl create -f jenkins-k8s/jenkins-pvc.yaml --namespace jenkins
- Deploy Jenkins on K8s cluster:

      kubectl create -f jenkins-k8s/jenkins-deployment.yaml --namespace jenkins
- Create service for Jenkins:

      kubectl create -f jenkins-k8s/jenkins-svc.yaml --namespace jenkins

> *Note*: I am using LoadBalancer as a type under spec of service. If you don't have load-balancer on your K8s cluster, you could change it to NodePort in `jenkins-k8s/jenkins-svc.yaml`
- Get the default password for logging in first time to Jenkins:
  
  Jenkins is going to set default password and you can find it under the logs of pod created by the Jenkins deployment. First find the pod name by `kubectl get pods -n jenkins`. It should start with `jenkins-deployment-` followed by universally unique identifiers (also known as UUIDs). After identifying the pod, check the logs for this particular pod to get the password:
 

      kubectl logs -n jenkins jenkins-deployment-b89c6f57d-gblmx

> *Note*: Replace pod name, in this case `jenkins-deployment-b89c6f57d-gblmx`, with your's

-  Create ClusterRole and ClusterRoleBinding for allowing Jenkins to take VolumeSnapshot and other associated operations:

       kubectl create -f jenkins-k8s/jenkins-rbac-snapshot-controller.yaml --namespace jenkins
- To allow running docker build within Jenkins, you need to allow pods to access `/var/run/docker.sock` file, located on K8s nodes where Jenkins application is running:

      sudo chmod 777 /var/run/docker.sock

> *Warning*: By executing above command on K8s nodes, you are exposing docker.sock file to all users and services

- Add Docker and GitHub credentials in Jenkins:
  
  You need to create Docker and GitHub credentials allowing Jenkins to push container image to Docker repository and pull / push changes to GitHub repository that you are going to use for the project. Name these credentials as `docker_login` and `dedmari_github`. These credentials are going to be used by the Jenkins pipeline, provided with this repository. If you are not aware of setting global credentials in Jenkins, please visit [https://www.jenkins.io/doc/book/using/using-credentials/#adding-new-global-credentials](https://www.jenkins.io/doc/book/using/using-credentials/#adding-new-global-credentials) for further information
- Jenkins plugins needed:

  You need to install [Docker Pipeline](https://plugins.jenkins.io/docker-workflow/) plugin. If you are not familiar with installing Jenkins plugins, please visit [https://www.jenkins.io/doc/book/managing/plugins/#from-the-web-ui](https://www.jenkins.io/doc/book/managing/plugins/#from-the-web-ui)

## Setup K8s secret for Kaggle credentials
In this use-case we are using [**DJIA 30 Stock Time Series**](https://www.kaggle.com/szrlee/stock-time-series-20050101-to-20171231) Kaggle dataset. We need to create a K8s secret in kubeflow namespace that holds the Kaggle credentials and allows to download data from Kaggle. To create a new token, go to Kaggle account and under `Account` click on the `Create New API Token` button. This will download a fresh authentication token (consisting username and key) onto your machine. We are storing base64 encrypted kaggle usrername and key in the secret yaml file. You can encrypt using [https://www.base64encode.org/](https://www.base64encode.org/) or create a python script locally and use [base64](https://docs.python.org/3/library/base64.html) python module.
Replace 'username' and 'key' in `kaggle-secret/muneer-kaggle-credentials.yaml` with your base64 encrypted values.

Finally, create secret in kubeflow namespace using `kaggle-secret/muneer-kaggle-credentials.yaml`:

    kubectl create -f kaggle-secret/muneer-kaggle-credentials.yaml -n kubeflow

## Deploy and setup TFServe 
All the files relevant to TFServe is located at `tfserve-config` directory in this repository
 - Create PVC, `fintech-model-pvc` for TFServe to store model:
   This PVC is going to be pre-loaded with trained model at the time of TFServe deployment. Later, this will be automatically updated when you train new models.
   

       kubectl create -f tfserve-config/tf-serve-fintech-pvc.yaml -n kubeflow
- Copy pre-trained model with model configuration to PVC:
	- Create a temporary pod `copy-model-to-tfserve`, to copy model and model configuration to the PVC created earlier:
	

		    kubectl create -f tfserve-config/tf-serve-copy-model-pod.yaml -n kubeflow
   - Copy pre-trained model and model config (local) to the PVC `fintech-model-pvc` using pod `copy-model-to-tfserve`: 
 

          kubectl cp tfserve-config/1 kubeflow/copy-model-to-tfserve:/mnt/
          kubectl cp tfserve-config/model_model_config kubeflow/copy-model-to-tfserve:/mnt/
  - Delete temporary pod `copy-model-to-tfserve`:

          kubectl delete -f tfserve-config/tf-serve-fintech-pvc.yaml -n kubeflow
- Deploy TFServe on K8s cluster:
  

      kubectl create -f tfserve-config/tf-serve-fintech-dep.yaml -n kubeflow
- Create service `fintech-service` for TFServe:
  

      kubectl create -f tfserve-config/tf-serve-fintech-svc.yaml -n kubeflow 
- Create virtual service `fintech-service` for TFServe:
  

      kubectl create -f tfserve-config/tf-serve-fintech-virtual-svc.yaml -n kubeflow 

## Directory structure
```bash
config/
├── pipeline.json        - Kubeflow pipeline config, model metrics and TFServe config. Update it as per your requirements

components/
├── data-consolidation            - Kubeflow pipeline component. Consist scripts and Docker file for downloading Kaggle dataset
├── timeseries-preprocessing      - Kubeflow pipeline component. Consist scripts and Docker file for data processing
├── timeseries-training           - Kubeflow pipeline component. Consist scripts and Docker file for training
```

## How it all works together:
In Jenkins, you need to create a Multibranch Pipeline and link Git repository to it. Before you do so, clone this git repository and push to your git repository with all the branches as that of this repository. If you are not familiar with Jenkins Multibranch Pipeline, visit [https://dzone.com/articles/implement-ci-for-multibranch-pipeline-in-jenkins](https://dzone.com/articles/implement-ci-for-multibranch-pipeline-in-jenkins) and follow the `Steps to Create a Simple Multibranch Pipeline Project` section only,  it will get you started. 

If you are interested to see it in action, please visit NVIDIA GTC 2021 session [E31919: From Research to Production—Effective Tools and Methodologies for Deploying AI Enabled Products](https://gtc21.event.nvidia.com/media/1_gt53r6i5?ncid=ref-spo-57504) , there you will find a demo📝 along with the basic walkthrough.
<!--stackedit_data:
eyJoaXN0b3J5IjpbNDAxMTAzNzU4LC05MzA1NjE2OTksMzQ4Nj
IxMDIxLDE5NDc3NDg0NSwxMzM3ODkwODk1LC02NzE4NTg4MCwy
OTI5ODQ3MDAsMTE1NjAzNjM5OCwtMTc5NjAzNDk3NCwtMjMwMT
gzMjMyLDYwOTkxNTM4MywtMTg0NjI1MDI4OCwtMTQ0NDAxMTk2
NCwxNDc2OTU5NjkyLC04MTc2NzcwMzIsMTczOTg2NjYxLC0xNj
M3MjI4MTE0LC0yMTY1NjIxMDQsLTE5NTg0NDI0MjAsLTEzNzA3
MTMzNjZdfQ==
-->
