import subprocess
import os
import sys
import tempfile

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
        print("❌ Set DOCKER_USER and DOCKER_PASS from Jenkins credentials")
        sys.exit(1)

    run(f'echo "{PASS}" | docker login -u "{USER}" --password-stdin')
    run(f"docker push {DOCKER_IMAGE}:{DOCKER_TAG}")

def load_kubeconfig():
    kubeconfig_content = os.getenv("KUBECONFIG_CONTENT")

    if not kubeconfig_content:
        print("❌ Missing KUBECONFIG_CONTENT (inject kubeconfig Jenkins secret file)")
        sys.exit(1)

    # Write kubeconfig to a temp file
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(kubeconfig_content.encode())
    temp_file.close()

    # Export KUBECONFIG to point to temp kubeconfig file
    os.environ["KUBECONFIG"] = temp_file.name
    print(f"✔ Loaded kubeconfig into {temp_file.name}")

def deploy_kubernetes():
    print("📦 Deploying to Kubernetes...")

    update_cmd = (
        f"kubectl set image deployment/myapp myapp={DOCKER_IMAGE}:{DOCKER_TAG} "
        f"--namespace default"
    )

    result = subprocess.run(update_cmd, shell=True)

    if result.returncode != 0:
        print("⚠ Deployment not found — applying new manifests")
        run("kubectl apply -f k8s-deployment.yml")

if __name__ == "__main__":
    print("🚀 Starting Python Pipeline...")

    build_docker_image()
    docker_login_and_push()

    load_kubeconfig()
    deploy_kubernetes()

    print("\n✅ Pipeline completed successfully!")
