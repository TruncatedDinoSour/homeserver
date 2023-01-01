#!/usr/bin/env bash

set -eux pipefail

main() {
    pyright .
    mypy .
    flake8 src/**.py
}

main "$@"
