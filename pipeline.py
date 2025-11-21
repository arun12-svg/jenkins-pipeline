import subprocess
import os
import sys
import tempfile

# -------------------------
# CONFIGURATION VARIABLES
# -------------------------
GIT_URL = "https://github.com/arun12-svg/jenkins-pipeline.git"
BRANCH = "main"

DOCKER_IMAGE = "arun054/myapp"
DOCKER_TAG = "v1"

K8S_DEPLOYMENT_FILE = "k8s-deployment.yml"


# -------------------------
# UTILITY RUNNER
# -------------------------
def run(cmd):
    print(f"\n---- Running: {cmd} ----")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"❌ Failed: {cmd}")
        sys.exit(result.returncode)


# -------------------------
# STAGE: GIT CHECKOUT
# -------------------------
def checkout_code():
    print("📥 Checking out GitHub repository...")

    # If folder exists, pull latest
    if os.path.exists(".git"):
        run("git pull")
    else:
        run(f"git clone -b {BRANCH} {GIT_URL} .")

    print("✔ Git checkout completed")


# -------------------------
# STAGE: BUILD DOCKER IMAGE
# -------------------------
def build_docker_image():
    print("🐳 Building Docker image...")
    run(f"docker build -t {DOCKER_IMAGE}:{DOCKER_TAG} .")


# -------------------------
# STAGE: DOCKERHUB LOGIN & PUSH
# -------------------------
def docker_login_and_push():
    print("🔐 Logging into DockerHub...")

    USER = os.getenv("DOCKER_USER")
    PASS = os.getenv("DOCKER_PASS")

    if not USER or not PASS:
        print("❌ ERROR: Jenkins must supply DOCKER_USER and DOCKER_PASS")
        sys.exit(1)

    run(f'echo "{PASS}" | docker login -u "{USER}" --password-stdin')
    run(f"docker push {DOCKER_IMAGE}:{DOCKER_TAG}")

    print("✔ Docker image pushed")


# -------------------------
# STAGE: LOAD KUBECONFIG
# -------------------------
def load_kubeconfig():
    print("🔐 Loading Kubernetes credentials...")

    kubeconfig_content = os.getenv("KUBECONFIG_CONTENT")

    if not kubeconfig_content:
        print("❌ ERROR: Jenkins must provide KUBECONFIG_CONTENT")
        sys.exit(1)

    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(kubeconfig_content.encode())
    temp_file.close()

    os.environ["KUBECONFIG"] = temp_file.name
    print(f"✔ Kubeconfig loaded at {temp_file.name}")


# -------------------------
# STAGE: DEPLOY TO K8S
# -------------------------
def deploy_kubernetes():
    print("🚀 Deploying to Kubernetes...")

    update_cmd = (
        f"kubectl set image deployment/myapp myapp={DOCKER_IMAGE}:{DOCKER_TAG} "
        f"--namespace default"
    )

    result = subprocess.run(update_cmd, shell=True)

    if result.returncode != 0:
        print("⚠ Deployment missing — applying manifest")
        run(f"kubectl apply -f {K8S_DEPLOYMENT_FILE}")

    print("✔ Kubernetes deployment updated")


# -------------------------
# MAIN PIPELINE
# -------------------------
if __name__ == "__main__":
    print("\n🚀 Starting Full Python Jenkins Pipeline...\n")

    checkout_code()
    build_docker_image()
    docker_login_and_push()
    load_kubeconfig()
    deploy_kubernetes()

    print("\n✅ Pipeline completed successfully!")
