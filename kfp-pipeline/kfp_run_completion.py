import os
import kfp

run_id = ''
with open('recent_run_id.txt') as run:
  run_id = run.read()
os.remove('recent_run_id.txt')

client = kfp.Client()
client.wait_for_run_completion(run_id=run_id, timeout=5000)

print(run_id)
