# Evidence-first RAG architecture

## Request and model path

Approved text files → bounded chunks → in-memory BM25 index → top passages → external chat endpoint → citation-ID check → answer or abstention

## Boundaries

- **Input:** Operator-approved `.md` and `.txt` files under `DOCUMENT_ROOT`. The corpus is indexed locally at process start/readiness.
- **Runtime:** `LLM_BASE_URL` and `LLM_MODEL` select a local or HTTPS OpenAI-compatible endpoint. `LLM_API_KEY` is supplied through a secret.
- **Failure behavior:** No documents make readiness 503. Missing endpoint configuration makes `/answer` return 503. Invalid or missing citation IDs produce an abstention.

The FastAPI process exposes `/health/live` for process liveness and `/health/ready` for local prerequisites. Each HTTP response carries a generated `X-Request-ID`, `Cache-Control: no-store`, and `X-Content-Type-Options: nosniff`. JSON request logs record method, path, status, request ID, and duration, never request bodies, query strings, credentials, or user data. Logs are local process telemetry, not a claim of production monitoring.

The [single Helm chart](../k8s/helm/evidence-rag-service/) provides rolling updates, probes, resource bounds, security contexts, optional HPA and NetworkPolicy, and a PDB. [Argo CD](../k8s/argocd/application.yaml) points to that chart. Values need environment review before deployment, especially image pull access, ingress peers, external inference egress, and artifact mounts.

## Limits

Citation IDs only prove that returned IDs were retrieved; they do not prove factual entailment or prevent every prompt injection. No private corpus or live endpoint is included.
