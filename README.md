<div align="center">
<h1>MLOps for Production Grade Machine Learning</h1>
<h2> MLOps: Fintech use-case </h2>
</div>
This repository contains the implementation of MLOps setup discussed in articles:

 - [Demystifying MLOps : Part 1](#)
 - [Demystifying MLOps : Part 2](#)

## Prerequisite
- [Kubernetes v1.18](https://v1-18.docs.kubernetes.io/docs/setup/) or above

## Install Trident, dynamic storage orchestrator, using helm
Install helm, if not already available:

    $curl [https://baltocdn.com/helm/signing.asc](https://baltocdn.com/helm/signing.asc) | sudo apt-key add -  
    $sudo apt-get install apt-transport-https --yes
    $echo "deb [https://baltocdn.com/helm/stable/debian/](https://baltocdn.com/helm/stable/debian/) all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
    $sudo apt-get update
    $sudo apt-get install helm
Download and extract Trident 20.01.1 installer:

    $wget https://github.com/NetApp/trident/releases/download/v21.01.1/trident-installer-21.01.1.tar.gz
    $tar -xf trident-installer-21.01.1.tar.gz
    $

- [NetApp Trident](https://netapp-trident.readthedocs.io/en/stable-v20.04/kubernetes/tridentctl-install.html)
- [Kubeflow v1.0](https://v1-0-branch.kubeflow.org/docs/started/getting-started/)

## Create a storage class (if not already) for Trident
This storage class will be used to create Persistent Volume Claims (PVCs) and store persistent data.
Lets use the underneath yaml fie to create storage class.


Copy  and store it as mlops_sc.yaml
 - create storage class
 
	`kubectl create sc  -f mlops.yaml`

## Install Jenkins with required plugins
We are using Jenkins for CI/CD. To install Jenkins on the same Kubernetes (K8s) cluster as that of Kubeflow, follow the steps mentioned underneath:

 - Create K8s namespace for Jenkins:
 
	 `kubectl create namespace jenkins`
- Create Persistent Volume Claim for Jenkins. It will 

<!--stackedit_data:
eyJoaXN0b3J5IjpbLTE5NTY4NDMxOTAsLTg0NTkyNzU5OCwtMT
AxMzAxNzA1MCwxNjA3MTE4MzQ4LC0xOTE5NjcxODc4LC0yMDg2
ODkwMyw2MTY0NTgzNTMsLTc0MDUzNjAzOCwtODEyNjIyMjc4XX
0=
-->