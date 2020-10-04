import os

with open('git_push.txt') as git_push:
  git_push_flag = git_push.read()
os.remove('git_push.txt')

# printing git_push_flag to access it in Jenkins
print(git_push_flag)
