#!/bin/sh
if [[ -z "${PORT}" ]]; then
    export PORT=5000
fi

gunicorn wsgi:app -w 2 --threads 2 -b 0.0.0.0:"${PORT}"