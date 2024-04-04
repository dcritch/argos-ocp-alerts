#!/usr/bin/env python
"""
script to display alerts from openshift clusters
"""

import json
import os
import ssl
import sys
import urllib.request
import yaml


def main():
    """
    do stuff
    """

    clusters = parse_config()
    alert_count = 0

    for cluster in clusters:
        clusters[cluster]["alerts"] = get_alerts(
            clusters[cluster]["url"], clusters[cluster]["token"]
        )
        if clusters[cluster]["alerts"]:
            clusters[cluster]["alerts"] = [
                a
                for a in clusters[cluster]["alerts"]
                if a["labels"]["severity"] in clusters[cluster]["severity"]
                and a["status"]["state"] != "suppressed"
            ]
            alert_count += len(clusters[cluster]["alerts"])

    if alert_count:
        print(f"openshift: <span color='red'>{alert_count}</span>")
    else:
        print(f"openshift: <span color='green'>{alert_count}</span>")

    for cluster in clusters:
        print("---")
        alerts = clusters[cluster]["alerts"]
        print(f"<b>{cluster}</b>: ", end="")
        if alerts:
            print(f"<span color='red'>{len(alerts)}</span>")
            for alert in alerts:
                annotations = alert["annotations"]
                if "description" in annotations.keys():
                    msg = annotations['description']
                if "message" in annotations.keys():
                    msg = annotations['message']
                msg = msg.replace('\n', '')
                print(f"--<i>{alert['labels']['alertname']}</i>: {msg} | length=128")
        else:
            print(f"<span color='green'>{len(alerts)}</span>")
            print("no active alerts")


def parse_config():
    """
    parse config file for list of clusters
    """
    config_file_path = os.path.expanduser("~/.config/ocp-alerts/clusters.yaml")
    try:
        with open(config_file_path, encoding="utf-8") as config_file:
            config = yaml.safe_load(config_file.read())
    except FileNotFoundError:
        sys.exit("could not open config file")
    return config["clusters"]


def get_alerts(url, token):
    """
    get alerts
    """
    headers = {"Authorization": f"Bearer {token}"}
    alerts_url = f"{url}/api/v2/alerts"
    ssl_context = ssl._create_unverified_context()
    request = urllib.request.Request(alerts_url, None, headers)
    try:
        with urllib.request.urlopen(request, context=ssl_context) as response:
            status_code = response.status
            alerts = response.read()
    except (urllib.error.URLError, urllib.error.HTTPError) as error:
        sys.exit(f"could not retrieve alerts: {error}")
    if status_code == 200 and alerts:
        return json.loads(alerts.decode("utf-8"))
    return None


main()
