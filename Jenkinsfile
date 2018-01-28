pipeline {
  agent {
    node {
      label 'windows'
    }
    
  }
  stages {
    stage('Dependencies') {
      steps {
        bat 'pip install -r requirements_websockets.txt'
        bat 'pip install -r requirements.txt'
      }
    }
    stage('Test') {
      steps {
        bat 'python setup.py test'
      }
    }
  }
}