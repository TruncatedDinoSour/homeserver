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
from flask import Blueprint
from flask import __version__ as flask_version  # type: ignore
from flask import render_template, request

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
    uname: os.uname_result = os.uname()

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        ram = psutil.virtual_memory()
        swap = psutil.swap_memory()
        drive = psutil.disk_usage("/")
        bat = psutil.sensors_battery()  # type: ignore

    return render_template(
        "stats/index.j2",
        stats=(
            {
                "OS": f"{get_distro_name()} {sys.platform}",
                "OS release": platform.release(),
                "OS version": platform.version(),
                "kernel": f"{uname.sysname} {uname.release} for {uname.machine}",
                "shell": os.environ.get("SHELL") or "/bin/sh",
            },
            {
                "time": str(dt.datetime.now()),
                "processes": str(len(tuple(psutil.process_iter()))),
                "uptime": f"{dt.timedelta(seconds=time_timestamp() - psutil.boot_time())}",
                "loadavg": ", ".join(map(str, psutil.getloadavg())),
            },
            {
                "RAM": storage_usage_fmt(ram),
                "swap": storage_usage_fmt(swap),
                "drive": storage_usage_fmt(drive, 30, "GB"),
                "batery": f"{bat.percent}%",  # type: ignore
            },
            {
                "CPU": f"{platform.processor()} [{psutil.cpu_percent()}%]",
                **{
                    f"CPU{core}": f"{usage}%" for core, usage in enumerate(psutil.cpu_percent(percpu=True, interval=1), 1)  # type: ignore
                },
            },
            {
                f"{name}[{t.label}]".lower(): f"{t.current} celsius"
                for name, temps in psutil.sensors_temperatures().items()
                for t in temps
            },
            {
                "ip": get_ip(),
                "pid": str(os.getpid()),
            },
            {
                "request": request.remote_addr or "(null)",
                "flask": flask_version,
                "python": sys.version,
                "api": str(sys.api_version),
            },
        ),
    )  # type: ignore
