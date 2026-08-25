#!/bin/bash
set -e

echo "Iniciando srv-email-google-sender..."
exec python app/main.py
