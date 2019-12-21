#!/usr/bin/env python3
import click
import os
from src.kubegraph import KubeGraph

CLI_DEFAULT_ARGS = {
    "kubeconfig": "~/.kube/config",
    "namespace": "default",
    "ignore_substrings": "pass,token,secret,hash,salt,_id,allow",
    "label_selector": ""
}


CLI_DEFAULT_ARGS = {
    "kubeconfig": "~/.kube/config",
    "namespace": "default",
    "ignore_substrings": "pass,token,secret,hash,salt,_id,allow",
    "label_selector": ""
}


CLI_DEFAULT_ARGS = {
    "kubeconfig": "~/.kube/config",
    "namespace": "default",
    "ignore_substrings": "pass,token,secret,hash,salt,_id,allow",
    "label_selector": ""
}


@click.command()
@click.option("--kubeconfig", default=os.getenv("KUBECONFIG", CLI_DEFAULT_ARGS['kubeconfig']), help="Path to kubeconfig file")
@click.option("--namespace", default=CLI_DEFAULT_ARGS['namespace'], help="Kubernetes namespace name")
@click.option("-A", "--all-namespaces", is_flag=True, help="Collect resources across all namespaces")
@click.option("--selector", default=CLI_DEFAULT_ARGS['label_selector'], help="Label selector for pods,services and ingresses")
@click.option('--skip-services', is_flag=True)
@click.option('--skip-ingresses', is_flag=True)
@click.option('--merge', is_flag=True)
@click.option("--ignored-substrings", default=CLI_DEFAULT_ARGS['ignore_substrings'], help="List of substrings for ignoring env names")
@click.option("-o", "--output", default="json", help="Output format", type=click.Choice(["json", "yaml", "graphviz"]))
def kubegraph_cli(**kwargs):
    """Print relatives of your kubernetes cluster based on pods environment variables."""
    if kwargs['all_namespaces']:
        kwargs['namespace'] = None
    kubegraph = KubeGraph(**kwargs)
    kubegraph.collect_pods()
    if not kwargs['skip_services']:
        kubegraph.collect_services()
    if not kwargs['skip_ingresses']:
        kubegraph.collect_ingresses()

    # kubegraph.merge('svc', 'pod')
    if kwargs['output'] == "json":
        import json
        print(json.dumps(kubegraph.json, indent=4, sort_keys=True))
    elif kwargs['output'] == "yaml":
        import yaml
        print(yaml.dump(kubegraph.json, default_flow_style=False, indent=4))
    elif kwargs['output'] == "graphviz":
        output = ""
        for (src, dsts) in kubegraph.json.items():
            for dst in dsts:
                output += '  "%s" -> "%s"\n' % (src, dst)
        print("digraph G {\n%s}" % output)
