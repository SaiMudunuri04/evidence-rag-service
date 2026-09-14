# Evidence RAG

[Architecture](docs/architecture.md) · [Operations runbook](docs/operations.md) · [Helm chart](k8s/helm/evidence-rag-service/) · [Argo CD application](k8s/argocd/application.yaml)

An independent service for retrieval, grounded generation, and citations. This repository contains executable source, tests,
a container, Helm release, Argo CD application, and a CI workflow that builds an
immutable GHCR image after tests pass. It is a reference implementation; it has not
been deployed to a user's AWS account or Kubernetes cluster.

## Run

```sh
python -m pip install -e '.[test]'
python -m pytest -q
ruff check .
helm lint k8s/helm/evidence-rag-service --strict
uvicorn service.app:app --reload
```

`/health/live` checks the process. `/health/ready` checks required local resources. Responses include a request ID and no-store/nosniff headers; JSON request logs omit bodies and query strings.
Configure data, model artifacts, and inference endpoints before serving traffic.

## Delivery

The workflow tests pull requests, then builds/pushes an image to GHCR on `main` and
updates the Helm image tag to the tested commit. Argo CD follows the single chart at [`k8s/helm/evidence-rag-service/`](k8s/helm/evidence-rag-service/).
Install `k8s/argocd/application.yaml` in a cluster with Argo CD, set environment-specific
Helm values, provide secrets through a cluster secret manager, and make the package
pullable by the cluster. Model/data volumes are configured through `volumes` and
`volumeMounts`; use `envFromSecretName` for credentials. The workflow does not
provision AWS or a cluster.

`.env.example` contains placeholders only. Never commit credentials or private data.

## Index and serve

Mount approved `.md` or `.txt` files under `DOCUMENT_ROOT`. The service chunks text, builds a BM25 index, retrieves source passages, and requires the generator's response to cite retrieved source IDs. An answer with missing or invalid citation IDs is replaced with an abstention. `citation_check` validates IDs; it is not a factual-entailment guarantee. Use a reviewed OpenAI-compatible inference endpoint over HTTPS or localhost.

```sh
DOCUMENT_ROOT=/path/to/documents LLM_BASE_URL=https://your-model.example/v1 LLM_MODEL=your-model uvicorn service.app:app --host 127.0.0.1
```

Mount documents read-only. Provide `LLM_API_KEY` through a Kubernetes secret, never Helm plaintext values. Add document access controls and a domain evaluation set for real enterprise use. No private documents or live inference service are included.
