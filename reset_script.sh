if [[ ! $(pgrep -f snmp_juniper_v2) ]]; then
    python3 /home/gts/network_measurements/snmp_juniper_v2.py 10.4.2.1 10.4.4.1 c24 t24 30
    echo "is working"
fi
