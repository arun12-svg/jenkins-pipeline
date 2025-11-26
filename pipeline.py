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
    DOCKER_USER = "arun054"

    # === ADD CREDENTIALS HERE ===
    DOCKER_USERNAME = "arun054"
    DOCKER_PASSWORD = "arunkumar"

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
    print("\n=== Logging into Docker Hub and pushing image ===\n")
    run_cmd(f'echo "{DOCKER_PASSWORD}" | docker login -u "{DOCKER_USERNAME}" --password-stdin')
    run_cmd(f"docker push {IMAGE_NAME}")

    # -------------------------
    # 4. Deploy to Kubernetes (Using pod.yaml template)
    # -------------------------

    # Load template pod.yaml
    with open("pod.yaml", "r") as f:
        template = f.read()

    # Replace dynamic values
    final_yaml = (
        template
        .replace("{{APP_NAME}}", APP_NAME)
        .replace("{{K8S_NAMESPACE}}", K8S_NAMESPACE)
        .replace("{{IMAGE_NAME}}", IMAGE_NAME)
    )

    # Save final rendered YAML
    with open("pod_rendered.yaml", "w") as f:
        f.write(final_yaml)

    # -------------------------
    # Delete old pod first
    # -------------------------
    print("\n=== Deleting old pod if it exists ===\n")
    run_cmd(f"kubectl delete pod {APP_NAME} -n {K8S_NAMESPACE} --ignore-not-found=true")

    # -------------------------
    # Apply new pod
    # -------------------------
    print("\n=== Creating new pod ===\n")
    run_cmd(f"kubectl apply -f pod_rendered.yaml -n {K8S_NAMESPACE}")

    # -------------------------
    # 5. Wait for Pod
    # -------------------------
    print("\n=== Waiting for Pod to become Running ===\n")

    for i in range(30):
        result = subprocess.getoutput(
            f"kubectl get pod {APP_NAME} -n {K8S_NAMESPACE} -o jsonpath='{{.status.phase}}'"
        )
        print(f"Status: {result}")
        if result == "Running":
            break
        time.sleep(2)
    else:
        print("❌ Pod did not reach Running state in time.")
        run_cmd(f"kubectl describe pod {APP_NAME} -n {K8S_NAMESPACE}")
        return

    # -------------------------
    # 6. Logs
    # -------------------------
    run_cmd(f"kubectl logs -n {K8S_NAMESPACE} {APP_NAME} --tail=50")

    print("\n=== Deployment Completed Successfully ===")


if __name__ == "__main__":
    main()
