import subprocess
import os
import sys

DOCKER_IMAGE = "arun054/myapp"
DOCKER_TAG = "v1"
GIT_URL = "https://github.com/arun12-svg/jenkins-pipeline.git"
BRANCH = "main"

def run(cmd):
    print(f"\n---- Running: {cmd} ----\n")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"❌ Failed: {cmd}")
        sys.exit(result.returncode)

def build_docker_image():
    run(f"docker build -t {DOCKER_IMAGE}:{DOCKER_TAG} .")

def docker_login_and_push():
    USER = os.getenv("DOCKER_USER")
    PASS = os.getenv("DOCKER_PASS")

    if not USER or not PASS:
        print("❌ Set DOCKER_USER and DOCKER_PASS environment variables in Jenkins credentials or environment variables")
        sys.exit(1)

    run(f'echo "{PASS}" | docker login -u "{USER}" --password-stdin')
    run(f"docker push {DOCKER_IMAGE}:{DOCKER_TAG}")

def deploy_kubernetes():
    kubeconfig = os.getenv("KUBECONFIG")
    if not kubeconfig:
        print("❌ Missing KUBECONFIG variable (Jenkins credentials)")
        sys.exit(1)

    os.environ["KUBECONFIG"] = kubeconfig

    update_cmd = (
        f"kubectl set image deployment/myapp myapp={DOCKER_IMAGE}:{DOCKER_TAG} "
        f"--namespace default"
    )
    result = subprocess.run(update_cmd, shell=True)
    if result.returncode != 0:
        run("kubectl apply -f k8s-deployment.yml")

if __name__ == "__main__":
    print("🚀 Starting Python Pipeline...")
    build_docker_image()
    docker_login_and_push()
    deploy_kubernetes()
    print("\n✅ Pipeline completed successfully!")
