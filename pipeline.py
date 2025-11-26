import os
import subprocess
import time
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
    DOCKER_USER = os.getenv("DOCKER_USERNAME", "arun054")  # default fallback
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
    docker_pass = os.getenv("DOCKER_PASSWORD")
    if DOCKER_USER and docker_pass:
        run_cmd(f'echo "{docker_pass}" | docker login -u "{DOCKER_USER}" --password-stdin')
        run_cmd(f"docker push {IMAGE_NAME}")
    else:
        raise Exception("DOCKER_USERNAME or DOCKER_PASSWORD not set!")

    # -------------------------
    # 4. Create Kubernetes Deployment YAML
    # -------------------------
    deployment_yaml = f"""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {APP_NAME}
  namespace: {K8S_NAMESPACE}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: {APP_NAME}
  template:
    metadata:
      labels:
        app: {APP_NAME}
    spec:
      containers:
      - name: {APP_NAME}
        image: {IMAGE_NAME}
        ports:
        - containerPort: 8000
"""
    with open("deployment.yaml", "w") as f:
        f.write(deployment_yaml)

    # Apply Deployment
    run_cmd(f"kubectl apply -f deployment.yaml -n {K8S_NAMESPACE}")

    # -------------------------
    # 5. Wait for Pod(s) to become Running
    # -------------------------
    print("\n=== Waiting for Pod(s) to become Running ===\n")
    for i in range(60):  # wait up to 2 minutes
        result = subprocess.getoutput(
            f"kubectl get pods -n {K8S_NAMESPACE} -l app={APP_NAME} -o jsonpath='{{.items[0].status.phase}}'"
        )
        print(f"Status: {result}")
        if result == "Running":
            break
        time.sleep(2)
    else:
        print("❌ Pod did not reach Running state in time.")
        run_cmd(f"kubectl describe deployment {APP_NAME} -n {K8S_NAMESPACE}")
        return

    # -------------------------
    # 6. Get Pod Logs
    # -------------------------
    pod_name = subprocess.getoutput(
        f"kubectl get pods -n {K8S_NAMESPACE} -l app={APP_NAME} -o jsonpath='{{.items[0].metadata.name}}'"
    )
    run_cmd(f"kubectl logs -n {K8S_NAMESPACE} {pod_name} --tail=50")

    print("\n=== Deployment Completed Successfully ===")

if __name__ == "__main__":
    main()
