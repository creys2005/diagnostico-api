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

def save_to_file(data):
    """Salva as informações coletadas em arquivos locais (TXT e JSON)."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    readable_timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    txt_filename = f"diagnostico_rede_{timestamp}.txt"
    json_filename = f"diagnostico_rede_{timestamp}.json"
    
    with open(txt_filename, "w", encoding="utf-8") as file:
        file.write(f"Coleta: {readable_timestamp}\n\n")
        for category, info in data.items():
            file.write(f"{category}\n")
            for key, value in info.items():
                file.write(f"{key}: {value}\n")
            file.write("\n")
    
    with open(json_filename, "w", encoding="utf-8") as json_file:
        json.dump({"Data e Hora da Coleta": readable_timestamp, **data}, json_file, indent=4, ensure_ascii=False)
    
    return txt_filename, json_filename

def main():
    system_info = get_system_info()
    network_info = get_network_info()
    
    data = {
        "Informações do Sistema": system_info,
        "Diagnóstico de Rede": network_info
    }
    
    txt_filename, json_filename = save_to_file(data)
    
    print(f"Diagnóstico salvo em:\n{os.path.abspath(txt_filename)}\n{os.path.abspath(json_filename)}")
    
if __name__ == "__main__":
    main()
