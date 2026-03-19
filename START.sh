#!/usr/bin/env bash
gunicorn pharmacy_project.wsgi:application --bind 0.0.0.0:$PORT