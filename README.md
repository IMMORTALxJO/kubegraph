# kubegraph
That tool prints relatives of your k8s cluster based on pods environment variables.

## Examples
Generate graph for the whole cluster with kubeconfig located in ~/.kube/config :
```
~» kubegraph
### http://www.webgraphviz.com/
digraph g{
    rankdir=LR;
    "notifications-service-12345678-abcde" -> "kafka://kafka-{1,2,3}.abcde.amazonaws.com"
    "backend-service.default" -> "pgsql://dev-server-postgres.rds.amazonaws.com"
    "backend-service.default" -> "kafka://kafka-{1,2,3}.abcde.amazonaws.com"
    "backend-service.default" -> "users-service.default"
    "users-service.default" -> "redis://dev.cache.amazonaws.com"
    "backend.example.com" -> "backend-service.default"
}
```

## Usage
```
Options:
  --kubeconfig TEXT               Path to kubeconfig file
  --ignore-substrings TEXT        List of substrings for ignoring env names
  --namespace TEXT                Kubernetes namespace name
  --skip-ingresses                Do not collect ingresses
  --skip-services                 Do not collect services
  --label-selector TEXT           Label selector for pods, services and
                                  ingresses
  --pod-label-selector TEXT       Label selector for pods
  --svc-label-selector TEXT       Label selector for services
  --ingress-label-selector TEXT   Label selector for ingresses
  --output-format [graphviz|mermaidjs|json]
                                  Output format
  --help                          Show this message and exit.
```

## Development
Run tests:
```
pip install pytest pycodestyle
pytest -v
```
Get coverage:
```
pip install pytest pycodestyle coverage
coverage erase
coverage run --branch --omit='./src/tests/*' --source=. -m pytest
coverage report
```
Run linter:
```
pip install pycodestyle
pycodestyle
```
