
import pytest
from sdi_manifest_bridge.core.enrichment import enrich_manifest

def test_enrich_manifest_basic():
    """
    Tests the enrichment of a manifest with basic required inputs.
    """
    user_input = {
        "mission": "mission-critical",
        "container_name": "data-processor",
        "image": "ubuntu:latest"
    }

    result = enrich_manifest(user_input)

    # Check metadata
    assert result["kind"] == "Pod"
    assert result["metadata"]["name"] == "mission-critical-data-processor"
    assert result["metadata"]["labels"]["mission"] == "mission-critical"
    assert result["metadata"]["annotations"]["male.sdi.dev/mission"] == "mission-critical"

    # Check spec
    assert result["spec"]["schedulerName"] == "sdi-scheduler"
    assert result["spec"]["priorityClassName"] == "real-time"
    assert result["spec"]["nodeSelector"]["role"] == "edge"

    # Check container details
    assert len(result["spec"]["containers"]) == 1
    container = result["spec"]["containers"][0]
    assert container["name"] == "data-processor"
    assert container["image"] == "ubuntu:latest"

def test_enrich_manifest_with_all_options():
    """
    Tests the enrichment of a manifest with all optional fields provided.
    """
    user_input = {
        "mission": "long-running-job",
        "container_name": "ml-worker",
        "image": "tensorflow/tensorflow:latest",
        "labels": {
            "team": "ml-team",
            "project": "project-x"
        },
        "annotations": {
            "monitoring.prometheus.io/scrape": "true"
        },
        "accuracy": 0.95,
        "latency": 0.5,
        "energy": 0.8
    }

    result = enrich_manifest(user_input)

    # Check merged labels
    assert result["metadata"]["labels"]["mission"] == "long-running-job"
    assert result["metadata"]["labels"]["team"] == "ml-team"
    assert result["metadata"]["labels"]["project"] == "project-x"

    # Check merged annotations
    assert result["metadata"]["annotations"]["male.sdi.dev/mission"] == "long-running-job"
    assert result["metadata"]["annotations"]["monitoring.prometheus.io/scrape"] == "true"
    assert result["metadata"]["annotations"]["male.sdi.dev/accuracy"] == "0.95"
    assert result["metadata"]["annotations"]["male.sdi.dev/latency"] == "0.5"
    assert result["metadata"]["annotations"]["male.sdi.dev/energy"] == "0.8"

    # Check basic fields are still correct
    assert result["metadata"]["name"] == "long-running-job-ml-worker"
    assert result["spec"]["containers"][0]["name"] == "ml-worker"
    assert result["spec"]["containers"][0]["image"] == "tensorflow/tensorflow:latest"
