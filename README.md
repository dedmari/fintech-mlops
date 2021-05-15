<div align="center">
<h1>MLOps for Production Grade Machine Learning</h1>
<h2> MLOps: Fintech use-case </h2>
</div>
This repository contains the implementation of MLOps setup discussed in articles:

 - [Demystifying MLOps : Part 1](#)
 - [Demystifying MLOps : Part 2](#)

## Prerequisite
- [Kubernetes v1.18](https://v1-18.docs.kubernetes.io/docs/setup/) or above

## Install Trident (dynamic storage orchestrator) using helm
Install helm, if not already available:

    $curl [https://baltocdn.com/helm/signing.asc](https://baltocdn.com/helm/signing.asc) | sudo apt-key add -  
    $sudo apt-get install apt-transport-https --yes
    $echo "deb [https://baltocdn.com/helm/stable/debian/](https://baltocdn.com/helm/stable/debian/) all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
    $sudo apt-get update
    $sudo apt-get install helm
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

    $cp sample-input/<backend template>.json backend.json
    # Edit backend.json and fill out the template for your backend
    $vi backend.json
    $./tridentctl -n trident create backend -f backend.json

## Create a storage class for Trident
This storage class will be used to create Persistent Volume Claims (PVCs) and store persistent data.
Lets use the underneath yaml fie to create storage class.
The simplest storage class to start with is one based on the `trident-installer/sample-input/storage-class-csi.yaml.templ` file that comes with the installer, replacing `__BACKEND_TYPE__` with the storage driver name.

    $kubectl create -f sample-input/storage-class-basic-csi.yaml
 Kubeflow installation requires a default storage class. We can patch the storage class created above (if not already set to default):
 
    $kubectl patch storageclass basic-csi -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'

## Install Kubeflow v1.0
Visit [https://v1-0-branch.kubeflow.org/docs/started/k8s/kfctl-k8s-istio/](https://v1-0-branch.kubeflow.org/docs/started/k8s/kfctl-k8s-istio/) and follow the installation instructions 
## Deploying and setting up volume snapshot components on K8s
If your cluster does not come pre-installed with the correct volume-snapshot components, you may manually install these components by executing the following steps:

 - Install Snapshot Beta CRDs:
 
       $kubectl create -f https://raw.githubusercontent.com/kubernetes-csi/external-snapshotter/release-3.0/client/config/crd/snapshot.storage.k8s.io_volumesnapshotclasses.yaml
       $kubectl create -f https://raw.githubusercontent.com/kubernetes-csi/external-snapshotter/release-3.0/client/config/crd/snapshot.storage.k8s.io_volumesnapshotcontents.yaml
       $kubectl create -f [https://raw.githubusercontent.com/kubernetes-csi/external-snapshotter/release-3.0/client/config/crd/snapshot.storage.k8s.io_volumesnapshots.yaml
 - Install Snapshot Controller:
   
        $kubectl apply -f [https://raw.githubusercontent.com/kubernetes-csi/external-snapshotter/release-3.0/deploy/kubernetes/snapshot-controller/rbac-snapshot-controller.yaml
        $kubectl apply -f [https://raw.githubusercontent.com/kubernetes-csi/external-snapshotter/release-3.0/deploy/kubernetes/snapshot-controller/setup-snapshot-controller.yaml
## Setup K8s VolumeSnapshotClass
 For creating a Volume Snapshot, a [VolumeSnapshotClass](https://netapp-trident.readthedocs.io/en/stable-v20.01/kubernetes/concepts/objects.html#kubernetes-volumesnapshotclass-objects) must be set up. We will create a volume snapshot class and it will be used to achieve ML versioning by leveraging NetApp Snapshot technology.
 
 - In this repository, you will find a folder `netapp-snaphot-class-config` having a VolumeSnapshotClass yaml file, namely `netapp-volume-snapshot-class.yaml`. Let's create VolumeSnapshotClass  `netapp-csi-snapclass`  and set it to default VolumeSnapshotClass:
 
       $kubectl create -f netapp-snaphot-class-config/netapp-volume-snapshot-class.yaml

## Install Jenkins with required plugins
We are using Jenkins for CI/CD. To install Jenkins on the same Kubernetes (K8s) cluster as that of Kubeflow, follow the steps mentioned underneath:

 - Create K8s namespace for Jenkins:
 
	   kubectl create namespace jenkins
- Create Persistent Volume Claim for Jenkins. It will be used to store Jenkins application data. Trident is going to dynamically allocate Persistent Volume. All the 

<!--stackedit_data:
eyJoaXN0b3J5IjpbLTE2MzcyMjgxMTQsLTIxNjU2MjEwNCwtMT
k1ODQ0MjQyMCwtMTM3MDcxMzM2NiwtODA5OTE2NTM5LC02Mzg4
MjQzMjAsMTY2MzgxOTE2NCwyODY5ODYyMTgsLTE1ODkzODgyOD
YsLTE2NzkxMDU3ODAsLTE0MjY4OTA5MSw2Njc5NTA2MjAsMTUz
MzI1MTI5NSwtMTcyODk4MTA4LC04NDU5Mjc1OTgsLTEwMTMwMT
cwNTAsMTYwNzExODM0OCwtMTkxOTY3MTg3OCwtMjA4Njg5MDMs
NjE2NDU4MzUzXX0=
-->