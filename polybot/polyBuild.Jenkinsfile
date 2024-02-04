pipeline {
    agent any
    environment {
        ECR_URL = '933060838752.dkr.ecr.eu-central-1.amazonaws.com'
        IMAGE_NAME = 'labay-polybot'
        AWS_ECR_CREDENTIALS = credentials('AWS_ECR_PASSWORD')
    }

    stages {
        stage('Build') {
            steps {
                script {
                    // Build Polybot image
                    withCredentials([string(credentialsId: 'AWS_ECR_PASSWORD', variable: 'AWS_ECR_PASSWORD')]) {
                        sh '''
                            docker login --username AWS --password-stdin $AWS_ECR_PASSWORD $ECR_URL
                            docker build -t polybot:$BUILD_NUMBER polybot/
                            docker tag polybot:$BUILD_NUMBER $ECR_URL/$IMAGE_NAME:$BUILD_NUMBER
                            docker push $ECR_URL/$IMAGE_NAME:$BUILD_NUMBER
                        '''
                    }
                }
            }
        }
        stage('Trigger Deploy') {
            steps {
                build job: 'PolybotDeploy', wait: false, parameters: [
                    string(name: 'POLYBOT_IMAGE_URL', value: "$ECR_URL/$IMAGE_NAME:$BUILD_NUMBER")
                ]
            }
        }
    }
}
