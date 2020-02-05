#!groovy
def PROJECT_NAME = "waarnemingen-voertuigen"
def SLACK_CHANNEL = '#waarnemingen'
def PLAYBOOK = 'deploy-waarnemingen-voertuigen.yml'
def PLAYBOOK_INVENTORY = 'acceptance'
def PLAYBOOK_BRANCH = 'feature/deploy-waarnemingen-voertuigen'
def SLACK_MESSAGE = [
    "title_link": BUILD_URL,
    "fields": [
        ["title": "Project","value": PROJECT_NAME],
        ["title":"Branch", "value": BRANCH_NAME, "short":true],
        ["title":"Build number", "value": BUILD_NUMBER, "short":true]
    ]
]



pipeline {
    agent any

    environment {
        SHORT_UUID = sh( script: "uuidgen | cut -d '-' -f1", returnStdout: true).trim()
        COMPOSE_PROJECT_NAME = "${PROJECT_NAME}-${env.SHORT_UUID}"
        VERSION = env.BRANCH_NAME.replace('/', '-').toLowerCase().replace(
            'master', 'latest'
        )
    }

    stages {
        stage('Test') {
            steps {
                sh 'env | sort'
                sh 'make test'
            }
        }

        stage('Build') {
            steps {
                sh 'env | sort'
                sh 'make build'
            }
        }

        stage('Push and deploy') {
            when { 
                anyOf {
                    branch 'master'
                    buildingTag()
                    branch pattern: "release/.*", comparator: "REGEXP"
                }
            }
            stages {
                stage('Push') {
                    steps {
                        retry(3) {
                            sh 'make push'
                        }
                    }
                }

                stage('Deploy to acceptance') {
                    when { branch pattern: "release/.*", comparator: "REGEXP"}
                    steps {
                        sh 'echo Deploy acceptance'
                        build job: 'Subtask_Openstack_Playbook', parameters: [
                            string(name: 'PLAYBOOK', value: PLAYBOOK),
                            string(name: 'INVENTORY', value: PLAYBOOK_INVENTORY),
                            string(name: 'BRANCH', value: PLAYBOOK_BRANCH),
                            string(
                                name: 'PLAYBOOKPARAMS', 
                                value: "-e deployversion=${VERSION}"
                            )
                        ], wait: true
                    }
                }

                stage('Deploy to production') {
                    when { tag pattern: "[\\d+\\.]+-RC.*", comparator: "REGEXP"}
                    steps {
                        sh 'echo Deploy prod'
                    }
                }
            }
        }

    }
    post {
        always {
            sh 'make clean'
        }
        /* success { */
            /* slackSend(channel: SLACK_CHANNEL, attachments: [SLACK_MESSAGE <<  */
                /* [ */
                    /* "color": "#36a64f", */
                    /* "title": "Build succeeded :rocket:", */
                /* ] */
            /* ]) */
        /* } */
        /* failure { */
            /* slackSend(channel: SLACK_CHANNEL, attachments: [SLACK_MESSAGE <<  */
                /* [ */
                    /* "color": "#D53030", */
                    /* "title": "Build failed :fire:", */
                /* ] */
            /* ]) */
        /* } */
    }
}

