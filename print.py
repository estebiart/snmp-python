from pysnmp.hlapi import nextCmd, SnmpEngine, CommunityData, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity

# OIDs comunes para obtener la información básica
COMMON_OIDS = {
    "status": "1.3.6.1.2.1.25.3.5.1.1",  # Estado de la impresora
    "ip_address": "1.3.6.1.2.1.4.20.1.1",  # IP de la impresora
    "device_name": "1.3.6.1.2.1.1.5.0"  # Nombre del dispositivo
}

# MIBs específicos de marcas (ejemplo)
BRAND_OIDS = {
    "HP": {
        "model": "1.3.6.1.2.1.25.3.2.1.3",  # Modelo específico de HP
    },
    "Konica Minolta": {
        "toner_level": "1.3.6.1.2.1.25.3.5.1.2",  # Nivel de tóner para Konica Minolta
    },
}

def get_snmp_data(ip, oid):
    """Obtiene datos SNMP de un dispositivo en la red."""
    iterator = nextCmd(
        SnmpEngine(),
        CommunityData('public', mpModel=0),
        UdpTransportTarget((ip, 161)),
        ContextData(),
        ObjectType(ObjectIdentity(oid))
    )
    
    error_indication, error_status, error_index, var_binds = next(iterator)
    
    if error_indication:
        print(f"Error con {ip}: {error_indication}")
        return None
    elif error_status:
        print(f"Error con {ip}: {error_status}")
        return None
    else:
        for var_bind in var_binds:
            return var_bind.prettyPrint()

def scan_network_for_printers(network_prefix):
    """Escanea la red buscando impresoras en el rango dado."""
    for i in range(1, 255):  # Ajusta el rango según la red
        ip = f"{network_prefix}{i}"
        device_name = get_snmp_data(ip, COMMON_OIDS['device_name'])
        
        if device_name:
            print(f"Dispositivo encontrado: {device_name} en {ip}")
            return ip
    return None

def get_printer_info(ip):
    """Obtiene información básica de la impresora."""
    # Obtener el estado
    status = get_snmp_data(ip, COMMON_OIDS['status'])
    # Obtener la IP
    ip_address = get_snmp_data(ip, COMMON_OIDS['ip_address'])
    
    return {
        "status": status,
        "ip_address": ip_address
    }

def get_brand_specific_info(ip, brand):
    """Obtiene información específica de la marca de la impresora."""
    if brand in BRAND_OIDS:
        brand_oids = BRAND_OIDS[brand]
        brand_info = {}
        for key, oid in brand_oids.items():
            brand_info[key] = get_snmp_data(ip, oid)
        return brand_info
    return {}

# Ejemplo de uso
network_prefix = "192.168.1."  # Cambiar según la red
printer_ip = scan_network_for_printers(network_prefix)

if printer_ip:
    printer_info = get_printer_info(printer_ip)
    print(f"Información de la impresora: {printer_info}")
    
    # Supongamos que sabemos que es una impresora HP
    hp_info = get_brand_specific_info(printer_ip, "HP")
    print(f"Información específica de HP: {hp_info}")
