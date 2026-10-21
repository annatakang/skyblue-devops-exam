#!/usr/bin/env bash
set -euo pipefail

namespace="${1:?Specify deployment namespace}"

case "$namespace" in
  dev) credential="${KUBE_CONFIG_DEV:?Missing KUBE_CONFIG_DEV}" ;;
  qa) credential="${KUBE_CONFIG_QA:?Missing KUBE_CONFIG_QA}" ;;
  staging) credential="${KUBE_CONFIG_STAGING:?Missing KUBE_CONFIG_STAGING}" ;;
  prod) credential="${KUBE_CONFIG_PROD:?Missing KUBE_CONFIG_PROD}" ;;
  *) echo "Unsupported namespace"; exit 1 ;;
esac

umask 077
KUBECONFIG="$(mktemp)"
export KUBECONFIG
trap 'rm -f "$KUBECONFIG"' EXIT
printf '%s' "$credential" | base64 --decode > "$KUBECONFIG"
unset credential

kubectl get secret skyblue-jwt --namespace "$namespace" >/dev/null

helm upgrade --install skyblue ./helm/skyblue \
  --namespace "$namespace" \
  --set-string image.tag="$CI_COMMIT_SHA" \
  --wait \
  --timeout 5m

for service in gateway users orders; do
  kubectl rollout status "deployment/skyblue-${service}" \
    --namespace "$namespace" --timeout=180s
done

kubectl get pods,pvc --namespace "$namespace"

gateway_ip="$(kubectl get service skyblue-gateway --namespace "$namespace" --output=jsonpath='{.spec.clusterIP}')"

python3 scripts/integration.py "http://${gateway_ip}:8000" "$namespace"
