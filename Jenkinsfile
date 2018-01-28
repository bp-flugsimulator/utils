pipeline {
  agent {
    node {
      label 'windows'
    }
    
  }
  stages {
    stage('Dependencies') {
      steps {
        bat 'python install.py --upgrade'
      }
    }
    stage('Test') {
      steps {
        bat 'python setup.py test'
      }
    }
  }
}