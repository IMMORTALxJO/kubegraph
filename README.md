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
  --namespace TEXT                Kubernetes namespace name
  --all-namespaces                Collect resources across all namespaces
  --label-selector TEXT           Label selector for pods,services and
                                  ingresses
  --collect-services / --skip-services
  --collect-ingresses / --skip-ingresses
  --ignored-substrings TEXT       List of substrings for ignoring env names
  -o, --output-format [json|yaml|graphviz]
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
coverage run --branch --omit='./tests/*' --source=. -m pytest
coverage report
```
Run linter:
```
pip install pycodestyle
pycodestyle
```
