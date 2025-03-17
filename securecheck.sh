#!/bin/bash

# Function to check firewall status
check_firewall() {
    echo "Checking firewall status..."
    if [[ "$(uname -s)" == "Linux" ]]; then
        if command -v ufw &> /dev/null; then
            ufw status | grep -q "Status: active" && echo "Firewall is enabled" || echo "Firewall is disabled"
        else
            echo "UFW firewall not installed."
        fi
    elif [[ "$(uname -s)" == "Darwin" ]]; then
        sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate
    elif [[ "$(uname -s)" == "CYGWIN" || "$(uname -s)" == "MINGW" ]]; then
        netsh advfirewall show allprofiles | grep "State"
    else
        echo "Unsupported OS for firewall check."
    fi
}

# Function to check open ports
check_open_ports() {
    echo "Checking open ports..."
    netstat -tulnp 2>/dev/null | awk '{print $4}' | grep -Eo '[0-9]{1,5}' | sort -nu
}

# Function to check CPU usage and temperature
check_cpu_health() {
    echo "Checking CPU health..."
    echo "CPU Usage: $(top -bn1 | grep 'Cpu(s)' | awk '{print $2 + $4}')%"
    if [[ -f /sys/class/thermal/thermal_zone0/temp ]]; then
        echo "CPU Temperature: $(($(cat /sys/class/thermal/thermal_zone0/temp) / 1000))°C"
    else
        echo "CPU Temperature: Not Available"
    fi
}

# Function to check memory usage
check_memory_health() {
    echo "Checking memory health..."
    free -h | awk '/Mem:/ {print "Total Memory: "$2", Used Memory: "$3", Available Memory: "$4}'
}

# Function to check disk health
check_disk_health() {
    echo "Checking disk health..."
    df -h | grep '^/'
    if command -v smartctl &> /dev/null; then
        smartctl -H /dev/sda | grep "SMART overall-health"
    else
        echo "SMART monitoring tools not installed."
    fi
}

# Function to check battery health
check_battery_health() {
    echo "Checking battery health..."
    if [[ -d /sys/class/power_supply/BAT0 ]]; then
        cat /sys/class/power_supply/BAT0/capacity
    else
        echo "Battery not found."
    fi
}

# Function to check system updates
check_security_updates() {
    echo "Checking for system updates..."
    if command -v apt &> /dev/null; then
        apt list --upgradable 2>/dev/null | grep -q "upgradable" && echo "Updates Available" || echo "System is up to date"
    elif command -v yum &> /dev/null; then
        yum check-update > /dev/null && echo "Updates Available" || echo "System is up to date"
    elif command -v brew &> /dev/null; then
        brew outdated && echo "Updates Available" || echo "System is up to date"
    else
        echo "Unknown package manager for updates check."
    fi
}

# Main execution
clear
echo "=== SecureCheck: System Security & Health Scanner ==="
check_firewall
check_open_ports
check_cpu_health
check_memory_health
check_disk_health
check_battery_health
check_security_updates
