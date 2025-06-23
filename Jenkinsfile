// Jenkinsfile: Definisi Pipeline CI/CD untuk Aplikasi Multi-Lingkungan
// File ini mengatur alur otomatis dari build, push image, hingga deployment ke Dev dan Prod.

pipeline {
    // Menentukan agen eksekusi pipeline. 'any' berarti Jenkins akan menggunakan agen manapun yang tersedia.
    agent any

    // Mendefinisikan variabel lingkungan global yang akan digunakan di seluruh pipeline.
    environment {
        // ID kredensial untuk Docker Hub (disimpan di Jenkins Credentials Manager)
        DOCKER_CRED_ID = 'dockerhub-credentials'
        // ID kredensial untuk Kubeconfig (file konfigurasi Kubernetes, disimpan di Jenkins Credentials Manager)
        KUBECONFIG_CRED_ID = 'kubeconfig-file'
        // Nama lengkap image Docker Hub Anda (username/nama-repo)
        DOCKER_IMAGE_NAME = 'masjidan/my-new-demo-app'
        // URL repositori GitHub proyek Anda
        GITHUB_REPO_URL = 'https://github.com/MZidan31/new-multi-env-ci-cd.git'
        // ID kredensial untuk GitHub (Personal Access Token, disimpan di Jenkins Credentials Manager)
        GITHUB_CRED_ID = 'github-token'
    }

    // Mendefinisikan tahapan-tahapan (stages) dalam pipeline CI/CD.
    stages {
        // Tahap 1: Checkout Kode Sumber
        // Mendapatkan kode terbaru dari repositori GitHub.
        stage('Checkout Source Code') {
            steps {
                // Mengambil kode dari SCM (Source Code Management), dalam kasus ini GitHub.
                git branch: 'main', credentialsId: env.GITHUB_CRED_ID, url: env.GITHUB_REPO_URL
            }
        }

        // Tahap 2: Build dan Push Image Docker
        // Membangun image Docker dari Dockerfile dan mendorongnya ke Docker Hub.
        stage('Build and Push Docker Image') {
            steps {
                script {
                    def imageTag // Variabel untuk menyimpan tag image Docker

                    // Menentukan tag image berdasarkan pemicu pipeline (branch 'main' atau tag Git).
                    if (env.BRANCH_NAME == 'main') {
                        imageTag = "latest" // Jika dari branch 'main', gunakan tag 'latest'
                    } else if (env.TAG_NAME) {
                        imageTag = env.TAG_NAME // Jika dari tag Git (misal: v1.0.0), gunakan nama tag tersebut
                    } else {
                        // Fallback jika bukan branch 'main' dan bukan tag (misal: branch fitur lainnya)
                        imageTag = "dev-${env.BUILD_NUMBER}" // Gunakan 'dev-' dan nomor build Jenkins
                    }

                    // Menggunakan kredensial Docker Hub untuk login.
                    withCredentials([usernamePassword(credentialsId: env.DOCKER_CRED_ID, usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
                        // Login ke Docker Hub menggunakan kredensial yang diambil.
                        sh "echo \$DOCKER_PASSWORD | docker login -u \$DOCKER_USERNAME --password-stdin"
                        // Membangun image Docker dengan nama dan tag yang ditentukan.
                        sh "docker build -t ${env.DOCKER_IMAGE_NAME}:${imageTag} ."
                        // Mendorong image yang telah dibangun ke Docker Hub.
                        sh "docker push ${env.DOCKER_IMAGE_NAME}:${imageTag}"
                    }
                    // Menyimpan tag image yang digunakan agar bisa diakses di tahap selanjutnya (Deploy to Prod).
                    env.IMAGE_TAG = imageTag
                }
            }
        }

        // Tahap 3: Deployment ke Lingkungan Dev
        // Menerapkan aplikasi ke namespace 'dev' di Kubernetes.
        stage('Deploy to Dev Environment') {
            // Kondisi: Hanya jalankan tahap ini jika pemicu pipeline adalah branch 'main'.
            when {
                branch 'main'
            }
            steps {
                script {
                    // Menggunakan file kubeconfig yang telah dimount ke dalam container Jenkins.
                    withCredentials([file(credentialsId: env.KUBECONFIG_CRED_ID, variable: 'KUBECONFIG_FILE_PATH')]) {
                        // Menyetel variabel lingkungan KUBECONFIG agar kubectl menggunakan file kredensial yang benar.
                        sh "export KUBECONFIG=${KUBECONFIG_FILE_PATH}"

                        // Menerapkan definisi namespace (jika belum ada/berubah).
                        sh "kubectl apply -f kubernetes/namespaces.yaml"
                        // Menunggu namespace 'dev' siap digunakan (opsional, tapi disarankan).
                        sh "kubectl wait --for=condition=ready namespace dev --timeout=30s"

                        // Menerapkan konfigurasi spesifik Dev: ConfigMap dan Secret.
                        sh "kubectl apply -f kubernetes/configmap-dev.yaml"
                        sh "kubectl apply -f kubernetes/secret-dev.yaml"

                        // Menerapkan deployment dan service untuk lingkungan Dev.
                        // Image 'latest' sudah diatur di deployment-dev.yaml.
                        sh "kubectl apply -f kubernetes/deployment-dev.yaml --namespace dev"
                        sh "kubectl apply -f kubernetes/service-dev.yaml --namespace dev"

                        // Menunggu hingga deployment 'demo-app-dev' siap dan semua pod berjalan.
                        sh "kubectl rollout status deployment/demo-app-dev --namespace dev"

                        echo "Aplikasi berhasil di-deploy ke lingkungan Development."
                        // Menampilkan URL untuk mengakses aplikasi Dev di Minikube.
                        sh "minikube service demo-app-service-dev --namespace dev --url"
                    }
                }
            }
        }

        // Tahap 4: Persetujuan Manual untuk Deployment ke Prod
        // Membutuhkan intervensi manual sebelum melanjutkan deployment ke Production.
        stage('Manual Approval for Production') {
            // Kondisi: Hanya jalankan tahap ini jika pemicu pipeline adalah tag Git apapun.
            when {
                tag '*' // Akan berjalan untuk setiap tag yang dibuat
            }
            steps {
                // Menampilkan prompt persetujuan di Jenkins UI. Pipeline akan berhenti di sini.
                input message: 'Apakah Anda yakin ingin men-deploy ke lingkungan Production?', ok: 'Deploy ke Prod'
            }
        }

        // Tahap 5: Deployment ke Lingkungan Prod
        // Menerapkan aplikasi ke namespace 'prod' di Kubernetes setelah persetujuan manual.
        stage('Deploy to Production Environment') {
            // Kondisi: Hanya jalankan tahap ini jika pemicu pipeline adalah tag Git apapun.
            when {
                tag '*'
            }
            steps {
                script {
                    // Memastikan IMAGE_TAG telah disetel dari tahap 'Build and Push Docker Image'.
                    if (!env.IMAGE_TAG) {
                        error "Kesalahan: IMAGE_TAG tidak disetel. Pastikan tahap 'Build and Push Docker Image' berjalan dengan benar."
                    }

                    // Menggunakan file kubeconfig untuk berinteraksi dengan Kubernetes.
                    withCredentials([file(credentialsId: env.KUBECONFIG_CRED_ID, variable: 'KUBECONFIG_FILE_PATH')]) {
                        sh "export KUBECONFIG=${KUBECONFIG_FILE_PATH}"

                        // Menerapkan definisi namespace (jika belum ada/berubah).
                        sh "kubectl apply -f kubernetes/namespaces.yaml"
                        // Menunggu namespace 'prod' siap.
                        sh "kubectl wait --for=condition=ready namespace prod --timeout=30s"

                        // Menerapkan konfigurasi spesifik Prod: ConfigMap dan Secret.
                        sh "kubectl apply -f kubernetes/configmap-prod.yaml"
                        sh "kubectl apply -f kubernetes/secret-prod.yaml"

                        // Untuk deployment ke Prod, kita akan membaca file deployment-prod.yaml,
                        // mengganti placeholder TAG_NAME dengan tag image yang sebenarnya (env.IMAGE_TAG),
                        // lalu mengaplikasikan output yang sudah diganti ke Kubernetes.
                        sh """
                          sed "s|TAG_NAME|${env.IMAGE_TAG}|g" kubernetes/deployment-prod.yaml | kubectl apply -f - --namespace prod
                        """
                        sh "kubectl apply -f kubernetes/service-prod.yaml --namespace prod"

                        // Menunggu hingga deployment 'demo-app-prod' siap.
                        sh "kubectl rollout status deployment/demo-app-prod --namespace prod"

                        echo "Aplikasi berhasil di-deploy ke lingkungan Production dengan image tag: ${env.IMAGE_TAG}."
                        // Menampilkan URL untuk mengakses aplikasi Prod di Minikube.
                        sh "minikube service demo-app-service-prod --namespace prod --url"
                    }
                }
            }
        }
    }

    // Bagian post-build: Akan selalu dijalankan setelah semua tahapan selesai (berhasil atau gagal).
    post {
        always {
            // Membersihkan workspace Jenkins setelah build selesai untuk menghemat ruang disk.
            deleteDir()
        }
    }
}
