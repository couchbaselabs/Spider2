#!/usr/bin/env python3
"""
Simple diagnostic script to check Couchbase connection
"""

import socket

def check_port(host, port):
    """Check if a port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

print("="*70)
print("Couchbase Connection Diagnostics")
print("="*70)
print()

# Common Couchbase ports
ports = {
    8091: "Web Console / REST API",
    8093: "Query Service (N1QL)",
    9000: "Custom/Non-standard",
    11210: "Data Service",
}

print("Checking localhost ports...")
print("-" * 70)

open_ports = []
for port, desc in ports.items():
    is_open = check_port("localhost", port)
    status = "✓ OPEN" if is_open else "✗ CLOSED"
    print(f"Port {port:5d} ({desc:30s}): {status}")
    if is_open:
        open_ports.append(port)

print()
print("="*70)
print("Result:")
print("="*70)

if not open_ports:
    print("❌ No Couchbase ports are open!")
    print()
    print("Couchbase Server is NOT running. Start it first:")
    print("  macOS:   open /Applications/Couchbase\\ Server.app")
    print("  Linux:   sudo systemctl start couchbase-server")
elif 8091 in open_ports:
    print("✅ Couchbase Server is running!")
    print()
    print("Use this connection string:")
    print("  cluster_url = \"couchbase://localhost\"")
    print()
    print("NOT:")
    print("  cluster_url = \"http://localhost:9000/\"  ❌")
else:
    print(f"⚠️  Found open ports: {open_ports}")
    print("But port 8091 (main Couchbase port) is not open.")
    print("Check your Couchbase configuration.")

print()

