#!/bin/bash
set -m
python app.py &
python consumer.py
fg %1