import usb.core
import usb.util
import socket
import json
import netifaces
import ipaddress

def find_usb_printers():
    """
    Scans connected USB devices for known POS printer vendor IDs.
    """
    printers = []
    devices = usb.core.find(find_all=True)
    known_vendor_ids = [0x04b8]  # Example: Epson's vendor ID
    for dev in devices:
        if dev.idVendor in known_vendor_ids:
            try:
                manufacturer = usb.util.get_string(dev, dev.iManufacturer)
            except Exception:
                manufacturer = "Unknown"
            try:
                product = usb.util.get_string(dev, dev.iProduct)
            except Exception:
                product = "Unknown"
            printers.append({
                'type': 'usb',
                'vendor_id': hex(dev.idVendor),
                'product_id': hex(dev.idProduct),
                'manufacturer': manufacturer,
                'product': product
            })
    return printers

def get_networks():
    """
    Retrieves the IPv4 networks for the PC's interfaces (excluding loopback).
    Returns a list of ipaddress.IPv4Network objects.
    """
    networks = []
    for iface in netifaces.interfaces():
        addrs = netifaces.ifaddresses(iface)
        if netifaces.AF_INET in addrs:
            for link in addrs[netifaces.AF_INET]:
                ip = link.get('addr')
                netmask = link.get('netmask')
                if ip and netmask and ip != "127.0.0.1":
                    try:
                        network = ipaddress.ip_network(f"{ip}/{netmask}", strict=False)
                        if network not in networks:
                            networks.append(network)
                    except Exception:
                        pass
    return networks

def generate_printer_stream():
    """
    Generator function that yields SSE events as printers are discovered.
    This function performs:
      - USB scanning,
      - Network scanning on each network found on the PC.
    Each network is scanned once and then the process stops.
    """
    yield "data: Starting printer discovery...\n\n"

    # USB Discovery
    usb_printers = find_usb_printers()
    if usb_printers:
        for printer in usb_printers:
            yield "data: Found USB printer: " + json.dumps(printer) + "\n\n"
    else:
        yield "data: No USB printers found.\n\n"

    # Network Discovery for each network interface found
    networks = get_networks()
    if networks:
        for network in networks:
            yield "data: Scanning network: " + str(network) + "\n\n"
            port = 9100  # Default port for many network POS printers.
            hosts_scanned = 0
            for host in network.hosts():
                ip = str(host)
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(0.3)  # Short timeout for feedback
                    result = s.connect_ex((ip, port))
                    s.close()
                    if result == 0:
                        yield "data: Found network printer at " + ip + "\n\n"
                except Exception:
                    pass
                hosts_scanned += 1
                # Optional: Provide progress update every 10 scanned addresses.
                if hosts_scanned % 10 == 0:
                    yield "data: Scanned " + str(hosts_scanned) + " addresses in network " + str(network) + "\n\n"
            yield "data: Finished scanning network: " + str(network) + "\n\n"
    else:
        yield "data: No network interfaces found.\n\n"

    yield "data: Discovery finished.\n\n"
