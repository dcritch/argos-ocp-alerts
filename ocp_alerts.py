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

    for cluster in clusters:
        clusters[cluster]["alerts"], clusters[cluster]["reachable"] = get_alerts(
            clusters[cluster]["url"],
            clusters[cluster]["token"],
            clusters[cluster]["severity"],
        )

    status = set_status(clusters)

    print(f" {status} | image='PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9Im5vIj8+Cjxzdmcgd2lkdGg9IjI1NnB4IiBoZWlnaHQ9IjIzN3B4IiB2aWV3Qm94PSIwIDAgMjU2IDIzNyIgdmVyc2lvbj0iMS4xIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiBwcmVzZXJ2ZUFzcGVjdFJhdGlvPSJ4TWlkWU1pZCI+Cgk8Zz4KCQk8cGF0aCBkPSJNNzQuODM5MjY4MSwxMDYuODkyOTI2IEwzMy45NzE0MTQ3LDEyMS43NjMzMTQgQzM0LjQ5NTgzMzYsMTI4LjMxNTM3NiAzNS42MjMzOTc4LDEzNC43ODc0NDIgMzcuMjExODkyLDE0MS4xMjg3MjEgTDc2LjAyOTA1MTYsMTI2Ljk5MjI2NSBDNzQuNzg0NjY3NywxMjAuNDQwMjAzIDc0LjM0MDI0NDgsMTEzLjY3MjI3OCA3NC44NDgxNTY2LDEwNi44OTE2NTYiIGZpbGw9IiNEQTI0MzAiPjwvcGF0aD4KCQk8cGF0aCBkPSJNMjU1LjQ0NDA3MSw2MS43MDIzNjE4IEMyNTIuNTkzNDE2LDU1LjgyMzI4MjcgMjQ5LjI5NzA2OCw1MC4xNDEwMTk0IDI0NS40Nzc1NzIsNDQuNzg2MzU5MSBMMjA0LjYyMTE0Niw1OS42NTY3NDcgQzIwOS4zNzY0Nyw2NC41MjAwMDI1IDIxMy4zNjM1NzgsNjkuOTg2NDAzMyAyMTYuNjI4MTgxLDc1LjgzMjQ2ODEgTDI1NS40NDUzNDEsNjEuNjk5ODIyMiBMMjU1LjQ0NDA3MSw2MS43MDIzNjE4IEwyNTUuNDQ0MDcxLDYxLjcwMjM2MTggWiIgZmlsbD0iI0RBMjQzMCI+PC9wYXRoPgoJCTxnPgoJCQk8cGF0aCBkPSJNMTgyLjk1MDI3NSw2MS40NjE0NDEzIEMxNzcuODA5Njk1LDU3LjAwMDU3OTIgMTcyLjAwNDAzMiw1My4xNTEwNjYyIDE2NS41NDE2NSw1MC4xMzY1NzUyIEwxNjUuNTM5MTEsNTAuMTM2NTc1MiBDMTI3LjU5ODA5OSwzMi40NDg1NDY2IDgyLjMzMDQ1OTQsNDguOTA0ODg5IDY0LjY0MjQzMDgsODYuODU4NTk4NSBDNjMuNjQ1NDkwMSw4OS4wMDAxNTEzIDYyLjc2MjU2MTEsOTEuMTY0NzE1NSA2MS45ODg2MDA2LDkzLjM0NjIxNTEgQzU5Ljc4MDkxNjQsOTkuNzY5MjY1NyA1OC40OTEyOTM2LDEwNi4zMzYwOSA1Ny45OTc4NTMzLDExMi44OTI0MSBMNTcuODUzOTI5NSwxMTIuOTQ1NiBDNTcuODUwMTYzMywxMTIuOTkzNjM1IDU3Ljg0NjQ0MDYsMTEzLjA0MTY3IDU3Ljg0Mjc2MTYsMTEzLjA4OTcwNCBMMzMuMjQ3MjIxNSwxMjIuMDM5NTEyIEwxNy40MjA3MzY2LDEyNy44ODg1MTMgQzE3LjQxODQ2MiwxMjcuODU5MzE0IDE3LjQxNjE5OCwxMjcuODMwMTE1IDE3LjQxMzk0NDcsMTI3LjgwMDkxNCBMMTYuOTc5OTg3MywxMjcuOTU4ODIyIEMxNS40NDM1NTQsMTA4LjUyMzU3NyAxOC43MTk1ODUxLDg4LjQ0NzA5MjcgMjcuNTMzMTI0Nyw2OS41NDc2OTQ0IEMyOC42ODcwMTM1LDY3LjA3MjQ4NDYgMjkuOTE3MTkyNCw2NC42NTY2MjA1IDMxLjIxOTU2ODYsNjIuMzAxNTkyMSBDNjAuMjczODE2MSw4LjE4NTY2MTYgMTI2LjM4MzU2OCwtMTQuNDM0MTYxMyAxODIuMTM4MzE3LDExLjk3MjUzNDIgQzE5My42NzgwMzcsMTcuNDQwNDgyNCAyMDMuOTExMDQ3LDI0LjYwOTQzNTcgMjEyLjY5NDUzNiwzMy4wNDU1MTEgQzIxOC42MDQwMSwzOC41MTIxMjE0IDIyMy44Nzg0MDUsNDQuNTMzNDk2OSAyMjguNDc1NzMxLDUwLjk4NjA1NzYgTDE4Ny42MTY3NjcsNjUuODU4OTg1IEMxODcuNDA2NTA5LDY1LjY0NDA4MjcgMTg3LjE5NDkyNSw2NS40MzAyNTM1IDE4Ni45ODIwMTgsNjUuMjE3NTE3MiBMMTg2Ljg2ODkwNiw2NS4yNTkzMzQ4IEMxODUuNjEwNDI2LDYzLjk1MjM2MDIgMTg0LjMwNDE2LDYyLjY4NDk3NzEgMTgyLjk1MDI3NSw2MS40NjE0NDEzIFoiIGZpbGw9IiNEQTI0MzAiPjwvcGF0aD4KCQkJPHBhdGggZD0iTTE5LjI2MTMyMTcsMTkzLjg5NjQ3NyBMMTkuMTk2ODk1MiwxOTMuOTE5OTMgQzEwLjY5NTcyMTQsMTgxLjk0OTcxOSA0LjUwODA4NTkxLDE2OC41MDE0ODUgMC45Mzg3MzU3MTQsMTU0LjM0NzI1MyBMMzkuNzYzNTEzOSwxNDAuMjA2OTg4IEwzOS43NjYwNTM1LDE0MC4yMDk1MjggQzM5Ljc3NDA1MTQsMTQwLjI1MTMwNiAzOS43ODIwODM4LDE0MC4yOTMwNzcgMzkuNzkwMTUwOCwxNDAuMzM0ODQxIEw0MC4wNDIyNiwxNDAuMjQxNjAxIEw0MC4wNDgxMDI2LDE0MC4yNTcxODEgQzQyLjA0MjI2NjIsMTUwLjgxNzgyMiA0Ni4xOTMzNjM2LDE2MC44OTIzOTQgNTIuMjQ1ODI0NSwxNjkuNzUwNjk1IEM1NC41NTM1MzMzLDE3My4wNDM5MTIgNTcuMTMyMTQxMywxNzYuMTY1NjUzIDU5Ljk2ODI0NTUsMTc5LjA3NzQ3OCBMNTkuODE0MDUzNSwxNzkuMTMzNjExIEM1OS45MTE2NjYzLDE3OS4yMzY1OTggNjAuMDA5NTkwMSwxNzkuMzM5MzMgNjAuMTA3ODI0MywxNzkuNDQxODAzIEwxOS42MjAyOTQ4LDE5NC40MTI1ODcgQzE5LjUwMDE3MSwxOTQuMjQwODUxIDE5LjM4MDUxMywxOTQuMDY4ODEzIDE5LjI2MTMyMTcsMTkzLjg5NjQ3NyBaIiBmaWxsPSIjRTgyNDI5Ij48L3BhdGg+CgkJCTxwYXRoIGQ9Ik0xNzMuNDY1NDg2LDE4My40NDY4NTggQzE1Mi40MTM5MzQsMTk2LjQ2NDI5IDEyNS40MTIzODcsMTk4Ljk3OTI1MiAxMDEuMzUxODgzLDE4Ny43NTg5NjEgQzkyLjg0MDU1MTMsMTgzLjc4OTYzIDg1LjQyNTAzOSwxNzguNDIxMDAyIDc5LjIzMzU5NDEsMTcyLjA2NDQ4NiBMMzguNDYyMjQzOSwxODYuOTA4MjA4IEMzOC41NjU5OTA4LDE4Ny4wNTQxMTcgMzguNjcwMDg0NSwxODcuMTk5ODA1IDM4Ljc3NDUyNDUsMTg3LjM0NTI3MiBMMzguNzU0MzQ4LDE4Ny4zNTI3MzMgQzQ5Ljk2NDQyMTUsMjAzLjM2OTM1IDY1LjI1NjU1MTIsMjE2Ljc1Njc4IDg0LjAyMTE1NDksMjI1LjY1MTIyMiBDMTI0LjQ5MDQ1NSwyNDQuODE0MzgyIDE3MC40MDc5MjcsMjM4LjE1MjI5OCAyMDMuNjU1NDc2LDIxMi4zNjY4IEMyMTguNTQzNDg2LDIwMS4yMTUyOTQgMjMwLjk3MTk5NSwxODYuMzUxMzYxIDIzOS4zNjgwMjcsMTY4LjM0Nzg0MSBDMjQ4LjE4NjY0NiwxNDkuNDUyMjUyIDI1MS40NDM2MzEsMTI5LjM4MzM4NyAyNDkuODgzMDcyLDEwOS45NjMzNzkgTDI0OC43NDc0NjQsMTEwLjM3NjU4NSBDMjQ4LjczMjExLDExMC4xNjg1NzQgMjQ4LjcxNjIxNywxMDkuOTYwNjM2IDI0OC42OTk3ODUsMTA5Ljc1Mjc3MSBMMjA4LjIxMDMwOCwxMjQuNzA5OTIzIEwyMDguMjEyMjU1LDEyNC43MTM4MTggQzIwNy41Njc2MTgsMTMzLjYzNzQ3MyAyMDUuMzQ5MzYzLDE0Mi41OTAzNDEgMjAxLjQwNTU4MywxNTEuMTczMTc2IEMxOTUuMDkxMTk5LDE2NC45MjY1MzkgMTg1LjI0MjAxMiwxNzUuODgyMTM1IDE3My40NjU0ODYsMTgzLjQ0Njg1OCBaIiBmaWxsPSIjREEyNDMwIj48L3BhdGg+CgkJCTxwYXRoIGQ9Ik0yMTguNTUyMzc5LDc1LjEyOTE5MTIgTDIxOS4xNTk0ODYsNzQuOTA4MTk1NyBMMjE5LjE1OTQ4Niw3NC45MDY5MjU5IEMyMjUuNTQ2NDc3LDg4LjA0OTE0MzggMjI5LjQ0NDcwMSwxMDIuMzM0MTYzIDIzMC42MTI4OTcsMTE2Ljk2MjAyMyBMMTg5Ljg0MDI3NywxMzEuNzk1NTg3IEMxODkuODQ3ODE2LDEzMS42OTQ0MjkgMTg5Ljg1NTE0OSwxMzEuNTkzMjc0IDE4OS44NjIyNzQsMTMxLjQ5MjEyMyBMMTg5LjA5MTI1MSwxMzEuNzc2OTgzIEMxOTAuMjAxMzUyLDExNi42ODkzNDUgMTg2LjgxNjUxNywxMDEuNjgzNTA1IDE3OS42NTczMzksODguNjU0NDIzNCBMMjE4LjIwNTExMyw3NC40MDQyMzA4IEwyMTguMjA3MDYsNzQuNDAwMzM1OCBDMjE4LjMyMjk5LDc0LjY0Mjg5NzIgMjE4LjQzODA5Nyw3NC44ODU4NTA3IDIxOC41NTIzNzksNzUuMTI5MTkxMiBaIiBmaWxsPSIjRTgyNDI5Ij48L3BhdGg+CgkJPC9nPgoJCTxwYXRoIGQ9Ik03NC44OTA2NzA3LDEwNi42NTQwMzEgTDM0LjMwOTY1OSwxMjEuNjUwMTMzIEMzNC44Mjk2NTM3LDEyOC4yNjAxMDQgMzUuOTQ5NDkyNSwxMzQuNzg2MzMxIDM3LjUyODk1MjIsMTQxLjE4MjA3MSBMNzYuMDc0Nzc4NiwxMjYuOTI0MDg4IEM3NC44MjgzNDkzLDEyMC4zMDI0MzIgNzQuMzgwNDEzNywxMTMuNDg2MDIyIDc0LjkwNjI1MTEsMTA2LjY1MDEzNiIgZmlsbD0iI0MyMjAzNSI+PC9wYXRoPgoJCTxwYXRoIGQ9Ik0yNTQuMjI2OTIsNjEuMDgyODIyOCBDMjUxLjM5NzEzNiw1NS4xNTQ0OTM0IDI0OC4xMjEzNjQsNDkuNDI0ODEzNyAyNDQuMzI5NDkyLDQ0LjAyNDI2OTEgTDIwMy43NTgyMTgsNTkuMDIwMzcxOCBDMjA4LjQ3OTA2OSw2My45MjYyMzk3IDIxMi40Mzg0Myw2OS40Mzc3OTQyIDIxNS42NzkxNDYsNzUuMzM0OTYzIEwyNTQuMjIxMDc3LDYxLjA3ODkyNzcgTDI1NC4yMjY5Miw2MS4wODI4MjI4IEwyNTQuMjI2OTIsNjEuMDgyODIyOCBaIiBmaWxsPSIjQzIyMDM1Ij48L3BhdGg+CgkJPHBhdGggZD0iTTM0LjMwODQ5MDQsMTIxLjY1MjY2NSBMNzQuNzkwMTc3NCwxMDYuODI0MDUyIEw3NC42MjQ2MzYsMTE0Ljk1NzAwMyBMMzUuNTY4NTUyNiwxMjkuNzA1NzY3IEwzNC4zMDI2NDc4LDEyMS42NDI5MjggTDM0LjMwODQ5MDQsMTIxLjY1MjY2NSBMMzQuMzA4NDkwNCwxMjEuNjUyNjY1IFoiIGZpbGw9IiNBQzIyM0IiPjwvcGF0aD4KCQk8cGF0aCBkPSJNMjAzLjc2NjAwOSw1OC44OTc0ODE3IEwyNDQuODc4Nyw0NC43ODk0NTk5IEwyNDkuMTUxNjE1LDUxLjIzNzc4NDEgTDIwOS4yMDU1MDQsNjUuMzU5NDM4NiBMMjAzLjc3MTg1MSw1OC44OTM1ODY2IEwyMDMuNzY2MDA5LDU4Ljg5NzQ4MTcgTDIwMy43NjYwMDksNTguODk3NDgxNyBaIiBmaWxsPSIjQUMyMjNCIj48L3BhdGg+CgkJPHBhdGggZD0iTTM4Ljc2Mzg5MDksMTg3LjIwMTAyIEw3OS4yOTQyNjY1LDE3Mi40NTIyNTYgTDkxLjU1MjExOTgsMTg0LjAxNjc4MiBMNDkuMDQ4ODgwMywxOTkuOTczMDI1IEwzOC43NjU4Mzg1LDE4Ny4xOTcxMjUgTDM4Ljc2Mzg5MDksMTg3LjIwMTAyIEwzOC43NjM4OTA5LDE4Ny4yMDEwMiBaIiBmaWxsPSIjQjkyMTM1Ij48L3BhdGg+CgkJPHBhdGggZD0iTTI0OS4zODA2NDcsMTA5Ljg2MTYzOSBMMjA4LjIxNTM3MSwxMjQuNzA1ODMzIEwyMDUuMTgzMDQzLDE0MS4xODQwMTggTDI0OS4wNzQ4ODIsMTI1LjU0MTMzIEwyNDkuMzg2NDksMTA5Ljg2MzU4NyBMMjQ5LjM4MDY0NywxMDkuODYxNjM5IEwyNDkuMzgwNjQ3LDEwOS44NjE2MzkgWiIgZmlsbD0iI0I5MjEzNSI+PC9wYXRoPgoJPC9nPgo8L3N2Zz4=' imageWidth=20")

    for cluster in clusters:
        print("---")
        alerts = clusters[cluster]["alerts"]
        print(f"<b>{cluster}</b>: ", end="")
        if not clusters[cluster]["reachable"]:
            print(f"<span color='yellow'>{len(alerts)}</span>")
        elif clusters[cluster]["reachable"] and len(alerts) > 0:
            print(f"<span color='red'>{len(alerts)}</span>")
        else:
            print(f"<span color='green'>{len(alerts)}</span>")
            print("--no active alerts")
        if alerts:
            for alert in alerts:
                annotations = alert["annotations"]
                msg = ""
                if "summary" in annotations.keys():
                    msg = annotations["summary"]
                if "description" in annotations.keys():
                    msg = annotations["description"]
                elif "message" in annotations.keys():
                    msg = annotations["message"]
                elif "summary" in annotations.keys():
                    msg = annotations["summary"]
                else:
                    msg = "No Data"
                msg = msg.replace("\n", "")
                print(f"--<b>{alert['labels']['alertname']}</b>: {msg} | length=128")


def set_status(clusters):
    """
    determine overall status of all clusters
    """
    status = "🟢"
    for cluster in clusters:
        if (not clusters[cluster]["reachable"]) and (status == "🟢"):
            status = "🟡"
        if clusters[cluster]["reachable"] and len(clusters[cluster]["alerts"]) > 0:
            status = "🔴"
    return status


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


def get_alerts(url, token, severity):
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
        error = str(error)
        error = error.replace(">", "")
        error = error.replace("<", "")
        alert = {
            "labels": {
                "alertname": "could not contact cluster",
                "severity": "critical",
            },
            "annotations": {"message": error},
            "status": {"state": "active"},
        }
        alerts = [alert]
        return alerts, False
    if status_code == 200 and alerts:
        alerts = json.loads(alerts.decode("utf-8"))
        alerts = [
            alert
            for alert in alerts
            if alert["labels"]["severity"] in severity
            and alert["status"]["state"] != "suppressed"
        ]
        return alerts, True

    return None


if __name__ == "__main__":
    main()
