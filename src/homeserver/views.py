#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""main homeserver views"""

from flask import Blueprint, render_template

from .config import SUBAPPS

views: Blueprint = Blueprint("views", __name__)


@views.get("/")
def index() -> str:
    return render_template("index.j2", subapps=SUBAPPS)
