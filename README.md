<div align="center">
<h1>MLOps for Production Grade Machine Learning</h1>
<h2> MLOps: Fintech use-case </h2>
</div>
This repository contains the implementation of MLOps setup discussed in articles:

 - [Demystifying MLOps : Part 1](#)
 - [Demystifying MLOps : Part 2](#)

## Prerequisite
- [Kubernetes v1.18](https://v1-18.docs.kubernetes.io/docs/setup/) or above
- [NetApp Trident](https://netapp-trident.readthedocs.io/en/stable-v20.04/kubernetes/tridentctl-install.html)
- [Kubeflow v1.0](https://v1-0-branch.kubeflow.org/docs/started/getting-started/)

## Create a storage class (if not already) for Trident
This storage class will be used to create Persistent Volume Claims (PVCs) 
## Install Jenkins with required plugins
We are using Jenkins for CI/CD. To install Jenkins on the same Kubernetes (K8s) cluster as that of Kubeflow, follow the steps mentioned underneath:

 - Create K8s namespace for Jenkins:
 
	 `kubectl create namespace jenkins`
- Create Persistent Volume Claim for Jenkins. It will 

<!--stackedit_data:
eyJoaXN0b3J5IjpbMTA0MTY0MDI0LDE2MDcxMTgzNDgsLTE5MT
k2NzE4NzgsLTIwODY4OTAzLDYxNjQ1ODM1MywtNzQwNTM2MDM4
LC04MTI2MjIyNzhdfQ==
-->