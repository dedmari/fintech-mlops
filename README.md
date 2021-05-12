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

## Install Jenkins with required plugins
We are using Jenkins for CI/CD. To install Jenkins on the same Kubernetes cluster as that of Kubeflow, follow the steps mentioned underneath:

 - Create kubernetes namespace for

<!--stackedit_data:
eyJoaXN0b3J5IjpbLTk0ODUxOTE1MSwxNjA3MTE4MzQ4LC0xOT
E5NjcxODc4LC0yMDg2ODkwMyw2MTY0NTgzNTMsLTc0MDUzNjAz
OCwtODEyNjIyMjc4XX0=
-->