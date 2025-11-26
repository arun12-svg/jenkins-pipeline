pipeline {
    agent { label 'agent-151' }

    stages {
        stage("Run Python Pipeline Script") {
            steps {
                sh "python3 pipeline.py"
            }
        }
    }
}
