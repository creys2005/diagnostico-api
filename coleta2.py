from flask import Flask, jsonify
import os
import socket
import psutil
import speedtest
import requests
import subprocess
import json
from ping3 import ping
from datetime import datetime
import platform

app = Flask(__name__)

def get_system_info():
    """Coleta informações do computador."""
    cpu_info = platform.processor()
    try:
        with open("/proc/cpuinfo", "r") as f:
            for line in f:
                if "model name" in line:
                    cpu_info = line.split(":")[1].strip()
                    break
    except FileNotFoundError:
        pass
    
    # Coleta informações dos discos
    disks = []
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disks.append({
                "Disco": partition.device,
                "Total (GB)": round(usage.total / (1024 ** 3), 2),
                "Usado (GB)": round(usage.used / (1024 ** 3), 2),
                "Disponível (GB)": round(usage.free / (1024 ** 3), 2),
                "Percentual Usado (%)": usage.percent
            })
        except PermissionError:
            continue
    
    system_info = {
        "Nome da Máquina": socket.gethostname(),
        "IP Local": socket.gethostbyname(socket.gethostname()),
        "Processador": cpu_info,
        "Modelo do Processador": platform.machine(),
        "Memória RAM (GB)": round(psutil.virtual_memory().total / (1024 ** 3), 2),
        "Uso de RAM (%)": psutil.virtual_memory().percent,
        "Uso de CPU (%)": psutil.cpu_percent(interval=1),
        "Discos": disks
    }
    return system_info

def get_network_info():
    """Coleta informações sobre a qualidade da rede."""
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        download_speed = round(st.download() / (1024 * 1024), 2)  # Convertendo para Mbps
        upload_speed = round(st.upload() / (1024 * 1024), 2)  # Convertendo para Mbps
        latency = round(st.results.ping, 2)
    except Exception:
        download_speed, upload_speed, latency = "Erro", "Erro", "Erro"
    
    try:
        ip_publico = requests.get("https://api64.ipify.org?format=json").json().get("ip", "Não encontrado")
    except Exception:
        ip_publico = "Erro ao obter IP público"
    
    jitter = round(st.results.server.get("latency", 0), 2) if hasattr(st, 'results') else "Indisponível"
    
    # Testando ping para múltiplos servidores
    ping_google = round(ping("8.8.8.8") * 1000, 2) if ping("8.8.8.8") else "Indisponível"
    ping_redeis = round(ping("nfb.redeis.com.br") * 1000, 2) if ping("nfb.redeis.com.br") else "Indisponível"
    
    return {
        "Velocidade de Download (Mbps)": download_speed,
        "Velocidade de Upload (Mbps)": upload_speed,
        "Latência (ms)": latency,
        "Jitter (ms)": jitter,
        "IP Público": ip_publico,
        "Ping Google (ms)": ping_google,
        "Ping RedeIS (ms)": ping_redeis
    }

@app.route('/coletar', methods=['GET'])
def coletar_dados():
    """Endpoint para coletar os dados e retornar como JSON."""
    system_info = get_system_info()
    network_info = get_network_info()
    
    data = {
        "Informações do Sistema": system_info,
        "Diagnóstico de Rede": network_info
    }
    
    return jsonify(data)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
