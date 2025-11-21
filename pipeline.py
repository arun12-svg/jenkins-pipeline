import subprocess
import os
import sys

DOCKER_IMAGE = "arun054/myapp"
DOCKER_TAG = "v1"

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
        print("❌ Missing DockerHub credentials! (DOCKER_USER / DOCKER_PASS)")
        sys.exit(1)

    run(f'echo "{PASS}" | docker login -u "{USER}" --password-stdin')
    run(f"docker push {DOCKER_IMAGE}:{DOCKER_TAG}")


def load_kubeconfig():
    kubeconfig_file = os.getenv("KUBECONFIG")

    if not kubeconfig_file or not os.path.exists(kubeconfig_file):
        print("❌ Kubeconfig file missing or invalid!")
        print(f"KUBECONFIG env value: {kubeconfig_file}")
        sys.exit(1)

    os.environ["KUBECONFIG"] = kubeconfig_file
    print(f"✔ Using kubeconfig file: {kubeconfig_file}")


def deploy_kubernetes():
    print("🚀 Deploying to Kubernetes...")

    update_cmd = (
        f"kubectl set image deployment/myapp myapp={DOCKER_IMAGE}:{DOCKER_TAG} "
        f"--namespace default"
    )

    result = subprocess.run(update_cmd, shell=True)

    if result.returncode != 0:
        print("⚠ Deployment not found — applying YAML manifests")
        run("kubectl apply -f k8s-deployment.yml")
    else:
        print("✔ Deployment updated successfully!")


if __name__ == "__main__":
    print("🚀 Starting Jenkins Python Pipeline...")

    build_docker_image()
    docker_login_and_push()
    load_kubeconfig()
    deploy_kubernetes()

    print("\n✅ Pipeline completed successfully!")
