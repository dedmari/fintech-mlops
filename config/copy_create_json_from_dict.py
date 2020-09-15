import json 

data = {}
data['pipeline_run_params'] = { 'embedding_size': '2',
                                 'num_classes': '2',
                                 'num_filters': '3',
                                 'sequence_length': '3'
                               }

with open('pipeline.json', 'w') as pipeline_config:
  json.dump(data, pipeline_config)
