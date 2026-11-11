pipeline {
    agent any

    environment {
        // Path absolut folder proyek di Windows Host.
        HOST_PROJECT_PATH = 'C:/cloud-project/cc-uts-resource-link-hub-main'
    }

    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    stages {

        // ── Stage 1: Checkout ─────────────────────────────────────────────
        stage('Checkout') {
            steps {
                echo '📥 Cloning source code from SCM...'
                checkout scm
                echo "✅ Checkout complete — Branch: ${env.GIT_BRANCH ?: 'N/A'} | Commit: ${env.GIT_COMMIT?.take(7) ?: 'N/A'}"
            }
        }

        // ── Stage 2: Syntax Check ─────────────────────────────────────────
        stage('Syntax Check') {
            steps {
                echo '🔍 Running syntax validation...'
                sh '''
                    echo "[1/2] Python syntax check -> app.py"
                    python3 -m py_compile app.py
                    echo "      ✅ app.py passed"

                    echo "[2/2] Docker Compose config validation"
                    docker-compose config
                    echo "      ✅ docker-compose.yml passed"
                '''
            }
        }

        // ── Stage 3: Build Image ──────────────────────────────────────────
        stage('Build Image') {
            steps {
                echo '🐳 Building Backend Docker Image...'
                sh 'docker-compose build --no-cache backend'
                echo '✅ Backend image built successfully'
            }
        }

        // ── Stage 4: Automated Deployment ────────────────────────────────
        stage('Automated Deployment') {
            steps {
                echo '🚀 Deploying Fullstack Application...'
                sh '''
                    # Hapus container lama dengan nama yang sama (jika ada)
                    docker rm -f resource-link-frontend resource-link-backend 2>/dev/null || true

                    # Deploy semua service
                    docker-compose up -d --remove-orphans
                    echo "✅ Services deployed successfully"
                '''
            }
        }

        // ── Stage 5: Health Check ─────────────────────────────────────────
        stage('Health Check') {
            steps {
                echo '🏥 Verifying Containers & Endpoints...'
                sh '''
                    sleep 5

                    # Hubungkan Jenkins ke app-net agar bisa reach container by name
                    docker network connect app-net jenkins-server 2>/dev/null || true

                    echo "--- Container Status ---"
                    docker-compose ps

                    echo "--- Checking Backend API (/links) ---"
                    curl -sf http://resource-link-backend:5000/links \
                      || curl -sf http://host.docker.internal:5000/links
                    echo "✅ Backend is healthy"

                    echo "--- Checking Frontend Nginx ---"
                    curl -sf http://resource-link-frontend:80 > /dev/null \
                      || curl -sf http://host.docker.internal:8081 > /dev/null
                    echo "✅ Frontend is healthy"

                    echo "✅ All services are UP and HEALTHY!"
                '''
            }
        }
    }

    // ── Post Actions ──────────────────────────────────────────────────────
    post {
        always {
            echo '📋 Final container status:'
            sh 'docker-compose ps || true'
        }
        success {
            echo '🎉 Pipeline SUCCEEDED! Application is live at http://localhost:8081'
        }
        failure {
            echo '❌ Pipeline FAILED — lihat log di atas untuk detail.'
        }
    }
}