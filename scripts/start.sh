#!/bin/bash

# Script de inicialização do container
echo "Iniciando srv-email-google-sender..."

# Iniciar cron em background
service cron start

# Iniciar a aplicação
echo "Iniciando aplicação Python..."
python app/main.py
