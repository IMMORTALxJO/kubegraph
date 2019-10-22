#!/usr/bin/env python3
import click
from src.kubegraph import KubeGraph


@click.command()
@click.option("--kubeconfig", default=KubeGraph.defaults['kubeconfig'], help="Path to kubeconfig file")
@click.option("--ignore-substrings", default=KubeGraph.defaults['ignore_substrings'], help="List of substrings for ignoring env names")
@click.option("--namespace", default=KubeGraph.defaults['namespace'], help="Kubernetes namespace name")
@click.option("--skip-ingresses", is_flag=True, help="Do not collect ingresses")
@click.option("--skip-services", is_flag=True, help="Do not collect services")
@click.option("--label-selector", default=KubeGraph.defaults['label_selector'], help="Label selector for pods,services and ingresses")
@click.option("--pod-label-selector", default=KubeGraph.defaults['pod_label_selector'], help="Label selector for pods")
@click.option("--svc-label-selector", default=KubeGraph.defaults['svc_label_selector'], help="Label selector for services")
@click.option("--ingress-label-selector", default=KubeGraph.defaults['ingress_label_selector'], help="Label selector for ingresses")
@click.option("--output-format", default=KubeGraph.defaults['output_format'], help="Output format", type=click.Choice(KubeGraph.output_formats))
def KubeGraphCLI(**kwargs):
    """Print relatives of your kubernetes cluster based on pods environment variables."""
    kubegraph = KubeGraph(**kwargs)
    kubegraph.init_client()
    if not kwargs['skip_services']:
        kubegraph.collect_services()
    kubegraph.collect_pods()
    if not kwargs['skip_ingresses']:
        kubegraph.collect_ingresses()
    kubegraph.generate_graph()
    kubegraph.output()
