# homeserver

> source code of my personal home server

## running

```sh
$ python3 src/main.py
```

## subapps

`subapp` is a concept in this project which allows for
multiple flask apps to be squished together, but also stay seperated,
it also has a prep system

to make a subapp make a file in `src/homeserver` folder called
`app_<subapp name>.py` and in it you should have at least one variable
of type `flask.Blueprint` called the same as your subapp, thats
the app youll be working with

if you need any prep to the pain app make a `prep_<your subapp name>`
function, its signature should be `(flask.Flask) -> None`

also, defining `__doc__` gives it a description, HTML is allowed

example subapp:

`app_example.py`

```py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""example <i>flask app</i>"""

from flask import Blueprint

example: Blueprint = Blueprint("example", __name__)


@example.get("/")
def index() -> str:
    return "<h1>example app</h1>"
```

all resources needed for subapps should go into the `subapp_res`
package
