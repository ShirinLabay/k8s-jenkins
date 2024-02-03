pipeline {
    agent any
    environment{
       ECR_URL = '933060838752.dkr.ecr.eu-central-1.amazonaws.com'
       IMAGE_NAME = 'labay-yolo5'
    }

    stages {
        stage('Build') {
            steps {
                sh '''
                aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin $ECR_URL
                docker build -t yolo:$BUILD_NUMBER yolo5/
                docker tag yolo:$BUILD_NUMBER $ECR_URL/$IMAGE_NAME:$BUILD_NUMBER
                docker push $ECR_URL/$IMAGE_NAME:$BUILD_NUMBER
                '''
            }
        }
        stage('Trigger Deploy') {
            steps {
                build job: 'YoloDeploy', wait: false, parameters: [
                    string(name: 'YOLO_IMAGE_URL', value: "$ECR_URL/$IMAGE_NAME:$BUILD_NUMBER")
        ]
    }
}

    }
}