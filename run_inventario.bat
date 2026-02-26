@echo off
cd /d "C:\Users\Administrador\Documents\GitHub\inventario_tecnologico"
call .venv\Scripts\activate
echo Iniciando servidor INVENTARIO TECH en puerto 8003...
waitress-serve --listen=127.0.0.1:8003 config.wsgi:application