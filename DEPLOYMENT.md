# SkyBlue DevOps exam

## Repositories and images

GitLab: https://gitlab.com/annatakang/skyblue-devops-exam
Original source: https://github.com/DataScientest/gitlab_devops_exams

DockerHub:
- https://hub.docker.com/r/annatakang77/skyblue-gateway
- https://hub.docker.com/r/annatakang77/skyblue-users
- https://hub.docker.com/r/annatakang77/skyblue-orders

## Architecture

Three FastAPI services: gateway, users, and orders.
K3s namespaces: dev, qa, staging, prod.
Each namespace contains its own JWT Secret and two local-path PVCs.
Users are stored in persistent JSON; orders use persistent SQLite.
The data-writing services use one replica and Recreate deployments.

## Pipeline

Helm validation -> image builds -> import checks and four unit tests
-> DockerHub publication -> dev -> qa -> staging -> manual prod.

Deployment jobs run application integration checks.
Non-production checks also create and retrieve a test order.
Production deployment requires manual execution on main.
Images are tagged with the full commit SHA.
Unit test results are uploaded as a JUnit report.

## Configuration

Protected GitLab variables:
DOCKERHUB_USERNAME, DOCKERHUB_TOKEN,
KUBE_CONFIG_DEV, KUBE_CONFIG_QA,
KUBE_CONFIG_STAGING, KUBE_CONFIG_PROD.

Kubeconfig variables contain base64-encoded service-account credentials.
Credentials were requested for 24 hours and must be renewed before expiry.
Each service account is restricted to its environment namespace.
JWT values are provisioned separately in skyblue-jwt Secrets.

Application variables:
- Gateway: SECRET_KEY, USERS_SERVICE_URL, ORDERS_SERVICE_URL
- Users: USERS_DB_PATH=/data/users.json
- Orders: DATABASE_URL=sqlite:///data/orders.sqlite3

## Deployment

Use Helm for installation and upgrades:

helm upgrade --install skyblue ./helm/skyblue \
  --namespace dev --set-string image.tag=FULL_COMMIT_SHA \
  --wait --timeout 5m

The k8s directory contains rendered reference manifests for each namespace.
Use the corresponding namespace when validating these files.
Do not apply them independently over a Helm-managed installation.

## Access and verification

kubectl port-forward -n dev service/skyblue-gateway 8081:8000

Open http://127.0.0.1:8081/docs from the machine running port-forward.
Deployment integration results appear in GitLab job logs.

Order persistence was verified by creating an order, restarting the
orders deployment, and retrieving the same order afterwards.

## Limitations

This exam uses a single-node cluster, local storage, legacy Python
dependencies, and starter demo accounts. It is not a highly available
production design. Probes and CI checks provide health verification;
continuous metrics collection, alerting, and backups are not configured.
