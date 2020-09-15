import json

with open('kubeflow.json') as kubeflow_config:
  data = json.load(kubeflow_config)
  print('kubeflow host: %s' % (data['kubeflow'][0]['host']))
