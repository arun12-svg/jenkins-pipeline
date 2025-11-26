import os
import subprocess
from datetime import datetime


def run_cmd(cmd):
    print(f"\n>>> Running: {cmd}")
    result = subprocess.run(cmd, shell=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Command failed: {cmd}")
    return result


def main():

    # -------------------------
    # CONFIG
    # -------------------------
    APP_NAME = "python-k8s-app"
    DOCKER_USER = "arun054"
    REPO_URL = "https://github.com/arun12-svg/jenkins-pipeline.git"
    K8S_NAMESPACE = "default"

    # Dynamic Version Tag
    VERSION = datetime.now().strftime("%Y%m%d-%H%M%S")
    IMAGE_NAME = f"{DOCKER_USER}/{APP_NAME}:{VERSION}"

    print(f"\n=== Using dynamic image: {IMAGE_NAME} ===\n")

    # -------------------------
    # 1. Clone Repository
    # -------------------------
    run_cmd(f"rm -rf repo && git clone {REPO_URL} repo")
    os.chdir("repo")

    # -------------------------
    # 2. Build Docker Image
    # -------------------------
    run_cmd(f"docker build -t {IMAGE_NAME} .")

    # -------------------------
    # 3. Login & Push Image
    # -------------------------
    docker_user = os.getenv("DOCKER_USERNAME")
    docker_pass = os.getenv("DOCKER_PASSWORD")

    if docker_user and docker_pass:
        run_cmd(f'echo "{docker_pass}" | docker login -u "{docker_user}" --password-stdin')
        run_cmd(f"docker push {IMAGE_NAME}")
    else:
        print("⚠ Skipping push (DOCKER_USERNAME or PASSWORD missing)")

    # -------------------------
    # 4. Deploy to Kubernetes
    # -------------------------
    pod_yaml = f"""
apiVersion: v1
kind: Pod
metadata:
  name: {APP_NAME}
  namespace: {K8S_NAMESPACE}
spec:
  containers:
    - name: {APP_NAME}
      image: {IMAGE_NAME}
      ports:
        - containerPort: 8000
"""

    with open("pod.yaml", "w") as f:
        f.write(pod_yaml)

    run_cmd(f"kubectl apply -f pod.yaml -n {K8S_NAMESPACE}")

    # -------------------------
    # 5. Verify Deployment
    # -------------------------
    run_cmd(f"kubectl get pods -n {K8S_NAMESPACE}")
    run_cmd(f"kubectl logs -n {K8S_NAMESPACE} {APP_NAME} --tail=50")

    print("\n=== Deployment Completed Successfully ===")


if __name__ == "__main__":
    main()
