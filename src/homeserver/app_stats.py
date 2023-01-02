#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""homeserver stats"""

import datetime as dt
import os
import platform
import socket
import sys
import warnings
from time import time as time_timestamp
from typing import Any

import psutil  # type: ignore
from distro import name as get_distro_name  # type: ignore
from flask import Blueprint, render_template, request  # type: ignore

stats: Blueprint = Blueprint("stats", __name__)


def get_ip() -> str:
    s: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)

    ip: str

    try:
        s.connect(("10.254.254.254", 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"

    s.close()
    return ip


def storage_usage_fmt(storage: Any, shift: int = 20, unit: str = "MB") -> str:
    return f"{storage.used >> shift} / {storage.total >> shift} {unit} ({storage.percent}%)"


@stats.get("/")
def index() -> str:
    uname = os.uname()

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        ram = psutil.virtual_memory()
        swap = psutil.swap_memory()
        drive = psutil.disk_usage("/")

    stats: dict[str, str] = {
        "OS": f"{get_distro_name()} {sys.platform}",
        "OS release": platform.release(),
        "OS version": platform.version(),
        "kernel": f"{uname.sysname} {uname.release} for {uname.machine}",
        "shell": os.environ.get("SHELL") or "/bin/sh",
        "CPU": f"{platform.processor()} [{psutil.cpu_percent()}%]",
    }

    for core, usage in enumerate(psutil.cpu_percent(percpu=True, interval=1), 1):  # type: ignore
        stats[f"CPU{core}"] = f"{usage}%"

    stats.update(
        {
            "RAM": storage_usage_fmt(ram),
            "swap": storage_usage_fmt(swap),
            "drive": storage_usage_fmt(drive, 30, "GB"),
            "ip": get_ip(),
            "pid": str(os.getpid()),
            "processes": str(len(tuple(psutil.process_iter()))),
            "uptime": f"{dt.timedelta(seconds=time_timestamp() - psutil.boot_time())}",
            "loadavg": ", ".join(map(str, psutil.getloadavg())),
            "request": request.remote_addr or "(null)",
        }
    )

    return render_template("stats/index.j2", stats=stats)  # type: ignore
