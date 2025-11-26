pipeline {
    agent { label 'agent-151' }

    environment {
        // Replace 'dockerhub-creds' with the actual Jenkins credentials ID for Docker Hub
        DOCKER_CREDENTIALS = credentials('dockerhub-creds')
    }

    stages {
        stage("Run Python Pipeline Script") {
            steps {
                // Pass username and password from Jenkins credentials to environment variables
                withEnv([
                    "DOCKER_USERNAME=${DOCKER_CREDENTIALS_USR}",
                    "DOCKER_PASSWORD=${DOCKER_CREDENTIALS_PSW}"
                ]) {
                    sh "python3 pipeline.py"
                }
            }
        }
    }
}
