import os
import psutil
import platform
import subprocess
import socket

def check_firewall():
    """Check if the system firewall is enabled."""
    try:
        if platform.system() == "Windows":
            result = subprocess.run(["netsh", "advfirewall", "show", "allprofiles"], capture_output=True, text=True)
            return "State ON" in result.stdout
        elif platform.system() == "Linux":
            result = subprocess.run(["ufw", "status"], capture_output=True, text=True)
            return "active" in result.stdout
        else:
            return "Unknown OS firewall check"
    except Exception as e:
        return f"Error checking firewall: {e}"

def check_open_ports():
    """Check open ports on the system."""
    open_ports = []
    for port in range(1, 1025):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        if sock.connect_ex(("127.0.0.1", port)) == 0:
            open_ports.append(port)
        sock.close()
    return open_ports

def check_cpu_health():
    """Check CPU usage and temperature."""
    cpu_usage = psutil.cpu_percent(interval=1)
    temp = "Not Available"
    if hasattr(psutil, "sensors_temperatures"):
        temps = psutil.sensors_temperatures()
        if "coretemp" in temps:
            temp = temps["coretemp"][0].current
    return {"CPU Usage (%)": cpu_usage, "CPU Temperature (°C)": temp}

def check_memory_health():
    """Check RAM usage."""
    mem = psutil.virtual_memory()
    return {"Total Memory (GB)": round(mem.total / (1024 ** 3), 2), "Used Memory (%)": mem.percent}

def check_disk_health():
    """Check disk usage and SMART status."""
    disk = psutil.disk_usage('/')
    disk_health = {"Total Disk (GB)": round(disk.total / (1024 ** 3), 2), "Used Disk (%)": disk.percent}
    try:
        result = subprocess.run(["smartctl", "-H", "/dev/sda"], capture_output=True, text=True)
        if "PASSED" in result.stdout:
            disk_health["SMART Status"] = "Healthy"
        else:
            disk_health["SMART Status"] = "Warning"
    except Exception:
        disk_health["SMART Status"] = "Unavailable"
    return disk_health

def check_battery_health():
    """Check battery health (if applicable)."""
    if not psutil.sensors_battery():
        return "No Battery Found"
    battery = psutil.sensors_battery()
    return {"Battery Percentage": battery.percent, "Charging": battery.power_plugged}

def check_security_updates():
    """Check if system updates are available."""
    try:
        if platform.system() == "Windows":
            result = subprocess.run(["powershell", "(Get-WindowsUpdate -ErrorAction SilentlyContinue).Count"], capture_output=True, text=True)
            return f"Pending updates: {result.stdout.strip()}" if result.stdout.strip().isdigit() else "Unable to fetch updates"
        elif platform.system() == "Linux":
            result = subprocess.run(["apt", "list", "--upgradable"], capture_output=True, text=True)
            return "Updates Available" if "upgradable" in result.stdout else "System is up to date"
        else:
            return "Unknown OS update check"
    except Exception as e:
        return f"Error checking updates: {e}"

def main():
    print("\n=== Security & Hardware Health Check ===")
    print(f"Firewall Enabled: {check_firewall()}")
    print(f"Open Ports: {check_open_ports()}")
    print(f"CPU Health: {check_cpu_health()}")
    print(f"Memory Health: {check_memory_health()}")
    print(f"Disk Health: {check_disk_health()}")
    print(f"Battery Health: {check_battery_health()}")
    print(f"System Updates: {check_security_updates()}")

if __name__ == "__main__":
    main()
