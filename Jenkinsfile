node {
  try {
    stage('Prepare') {
      sh "git config user.name 'dedmari'"
      sh "git config user.email 'muneer7589@gmail.com'"
    }
    stage('Build Tests') {
      echo "Some automated tests..."
    }
    stage('Build and Push Images') {
      if (env.BRANCH_NAME.startsWith("ds_task")) {
        echo "Some automated code tests..."
      }
      else if (env.BRANCH_NAME.startsWith("build-components")) {
        component1 = docker.build("muneer7589/fintech-dataset-download", "-f ${env.WORKSPACE}/components/data-consolidation/Dockerfile .")
        component2 = docker.build("muneer7589/fintech-preprocess-data", "-f ${env.WORKSPACE}/components/timeseries-preprocessing/Dockerfile .")
        component3 = docker.build("muneer7589/fintech-train", "-f ${env.WORKSPACE}/components/timeseries-training/Dockerfile .")

        /* Using DockerHub as docker registry. You need to registry before you can push image to your account. */
        /* Arguments for docker.Registry: Registry URL followed by Credential(e.g. docker_login) stored on Jenkins server */
        docker.withRegistry('https://registry.hub.docker.com', 'docker_login') {
          component1.push("${env.BUILD_NUMBER}")
          component1.push("latest")
        }
        docker.withRegistry('https://registry.hub.docker.com', 'docker_login') {
          component2.push("${env.BUILD_NUMBER}")
          component2.push("latest")
        }
        docker.withRegistry('https://registry.hub.docker.com', 'docker_login') {
          component3.push("${env.BUILD_NUMBER}")
          component3.push("latest")
        }
      }

    }
    stage('Kubeflow Pipeline Update') {
      if (env.BRANCH_NAME.startsWith("kf-pipeline")) {
        sh "python3.6 ${env.WORKSPACE}/kfp-pipeline/kfp_timeseries_prepro_train.py --build_num ${env.BUILD_NUMBER}"
      }
    }
    stage('Kubeflow Pipeline Run') {
      if (env.BRANCH_NAME.startsWith("training")) {
        def run_script_output = sh(script:"python3.6 ${env.WORKSPACE}/kfp-pipeline/kfp_run_pipeline.py", returnStdout:true)
        office365ConnectorSend webhookUrl: 'https://outlook.office.com/webhook/8ff9afd3-5134-49a0-8dca-be6884951125@4b0911a0-929b-4715-944b-c03745165b3a/JenkinsCI/6d2b6238d4b74f6ba1541496b8aad9ab/02438fa1-3250-4de7-a462-8238a6e99ca9',
            message: "Kubeflow Pipeline Run has been triggered. \n ${run_script_output}",
            status: 'Success'
      }
    }
    stage('kfpRunStatus') {
      if (env.BRANCH_NAME.startsWith("training")) {
        def run_id = sh(script:"python3.6 ${env.WORKSPACE}/kfp-pipeline/kfp_run_completion.py", returnStdout:true)
        office365ConnectorSend webhookUrl: 'https://outlook.office.com/webhook/8ff9afd3-5134-49a0-8dca-be6884951125@4b0911a0-929b-4715-944b-c03745165b3a/JenkinsCI/6d2b6238d4b74f6ba1541496b8aad9ab/02438fa1-3250-4de7-a462-8238a6e99ca9',
            message: "Kubeflow Pipeline Run has been finished. Run Id: ${run_id}",
            status: 'Success'
      }
      /* Updating pipeline config after run. Mainly used to update pvc names as kubeflow pipeline is prepends workspace name before volume name */
      /* Currently just testing pushing updates to git. Later this code is going to be executd only for training brancg, hence goes in "if" block above. */
      /* Later utilise script used to get new volume names with update_config script to automate updating newly created volume names */
      /* It can also be used to upload model metrics to git and run some-tests before deploying model to production */
      else {
        sh "python3.6 ${env.WORKSPACE}/config/test_jenkins_python_exec.py"
        sh "git checkout -B ds1"
        echo "PWD"
        sh "pwd"
        sh "cat ${env.WORKSPACE}/config/pipeline.json"
        sh "python3.6 ${env.WORKSPACE}/config/update_config.py"
        echo "After Update..."
        sh "cat ${env.WORKSPACE}/config/pipeline.json"
        sh "git status"
        /* sh "git checkout -B ds1" */

        withCredentials([usernamePassword(credentialsId: 'dedmari_github', passwordVariable: 'GIT_PASSWORD', usernameVariable: 'GIT_USERNAME')]) {

          sh ('''
                git config --local credential.helper "!f() { echo username=\\$GIT_USERNAME; echo password=\\$GIT_PASSWORD; }; f"
                git add .
                git commit -m 'testing pushing code using Jenkins pipeline'
                git push origin HEAD:ds1
          ''')
        }
      }
    }
    stage('deploy') {
      echo "stage2: deploy model in production..."
    }
  } finally {
    stage('cleanup') {
      echo "doing some cleanup..."
    }
  }
}
