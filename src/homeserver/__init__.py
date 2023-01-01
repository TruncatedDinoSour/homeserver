#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""homeserver"""

import os
from glob import glob

from flask import Flask, session

from . import config


def register_dynamic_routes(app: Flask) -> None:
    """registers index routes and dynamic routes on the specified app
    NOTE: this function is quite unsafe, i need a better way to register dynamic
          apps"""

    from .views import views

    app.register_blueprint(views, url_prefix="/")

    for subapp in glob(f"{__path__[0]}/app_*.py"):  # type: ignore
        mod_name: str = os.path.splitext(os.path.basename(subapp))[0]
        name: str = mod_name[4:]

        try:
            exec(f"""from .{mod_name} import prep_{name};prep_{name}(app)""")
        except ImportError:
            pass

        exec(f"from .{mod_name} import {name}, __doc__ as {name}_desc")

        config.SUBAPPS[name] = eval(f"{name}_desc") or "<i>no description provided</i>"
        app.register_blueprint(eval(name), url_prefix=f"/{name}")


def create_homeserver() -> Flask:
    """creates, configures and registers a new `homeserver` server"""

    os.makedirs(config.DB_DIR, exist_ok=True)

    app: Flask = Flask(__name__)

    @app.before_request
    def _() -> None:
        session.permanent = True

    app.config.update({   # type: ignore
        "SECRET_KEY": config.RANDOM.randbytes(config.SECRET_KEY_SIZE),
        "MAX_CONTENT_LENGTH": config.MAX_CONTENT_LENGTH,
    })

    register_dynamic_routes(app)

    return app
