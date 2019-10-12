# kubegraph
That tool prints relatives of your k8s cluster based on pods environment variables.

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
