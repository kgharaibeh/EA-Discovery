"""
Local Network Probe Script for EA Discovery.

Scans the local network subnet for active hosts and common services.
Uses async TCP connect probes — no credentials needed, safe read-only scan.
"""

import asyncio
import ipaddress
import json
import socket
import struct
import sys
import time
from datetime import datetime


COMMON_PORTS = {
    22: "SSH",
    53: "DNS",
    80: "HTTP",
    443: "HTTPS",
    445: "SMB",
    548: "AFP",
    554: "RTSP",
    631: "CUPS/IPP",
    1433: "SQL Server",
    1521: "Oracle",
    3306: "MySQL",
    3389: "RDP",
    5000: "UPnP/Dev Server",
    5432: "PostgreSQL",
    5900: "VNC",
    5985: "WinRM HTTP",
    5986: "WinRM HTTPS",
    6379: "Redis",
    7680: "WUDO",
    8080: "HTTP Proxy",
    8443: "HTTPS Alt",
    8883: "MQTT TLS",
    9090: "Prometheus/Mgmt",
    9100: "Printer",
    27017: "MongoDB",
    32400: "Plex",
    49152: "UPnP",
    62078: "iPhone Sync",
}

CONNECT_TIMEOUT = 1.5
PING_CONCURRENCY = 100
PORT_CONCURRENCY = 200


async def check_port(host: str, port: int, timeout: float = CONNECT_TIMEOUT) -> dict | None:
    try:
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=timeout,
        )
        writer.close()
        await writer.wait_closed()
        return {"port": port, "service": COMMON_PORTS.get(port, "unknown"), "state": "open"}
    except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
        return None


async def grab_banner(host: str, port: int, timeout: float = 2.0) -> str:
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=timeout,
        )
        banner = ""
        if port in (80, 8080, 8443, 443):
            writer.write(f"HEAD / HTTP/1.0\r\nHost: {host}\r\n\r\n".encode())
            await writer.drain()
        try:
            data = await asyncio.wait_for(reader.read(512), timeout=timeout)
            banner = data.decode("utf-8", errors="replace").strip()
        except asyncio.TimeoutError:
            pass
        writer.close()
        await writer.wait_closed()
        return banner[:200]
    except Exception:
        return ""


async def probe_host(host: str, semaphore: asyncio.Semaphore) -> dict | None:
    async with semaphore:
        try:
            _, writer = await asyncio.wait_for(
                asyncio.open_connection(host, 80),
                timeout=0.8,
            )
            writer.close()
            await writer.wait_closed()
            return {"host": host, "reachable": True}
        except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
            pass

        try:
            _, writer = await asyncio.wait_for(
                asyncio.open_connection(host, 443),
                timeout=0.8,
            )
            writer.close()
            await writer.wait_closed()
            return {"host": host, "reachable": True}
        except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
            pass

        try:
            _, writer = await asyncio.wait_for(
                asyncio.open_connection(host, 445),
                timeout=0.8,
            )
            writer.close()
            await writer.wait_closed()
            return {"host": host, "reachable": True}
        except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
            pass

        try:
            _, writer = await asyncio.wait_for(
                asyncio.open_connection(host, 22),
                timeout=0.8,
            )
            writer.close()
            await writer.wait_closed()
            return {"host": host, "reachable": True}
        except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
            pass

    return None


async def discover_hosts(subnet: str) -> list[str]:
    network = ipaddress.IPv4Network(subnet, strict=False)
    print(f"[*] Scanning {network} for live hosts ({network.num_addresses - 2} addresses)...")

    semaphore = asyncio.Semaphore(PING_CONCURRENCY)
    tasks = [probe_host(str(ip), semaphore) for ip in network.hosts()]
    results = await asyncio.gather(*tasks)

    live = [r["host"] for r in results if r is not None]
    print(f"[+] Found {len(live)} live hosts")
    return sorted(live, key=lambda x: ipaddress.IPv4Address(x))


async def scan_host_ports(host: str) -> dict:
    try:
        hostname = socket.getfqdn(host)
    except Exception:
        hostname = host

    sem = asyncio.Semaphore(PORT_CONCURRENCY)

    async def limited_check(port):
        async with sem:
            return await check_port(host, port)

    tasks = [limited_check(port) for port in COMMON_PORTS]
    results = await asyncio.gather(*tasks)
    open_ports = [r for r in results if r is not None]

    banners = {}
    for p in open_ports:
        banner = await grab_banner(host, p["port"])
        if banner:
            banners[p["port"]] = banner

    asset_type = infer_asset_type(open_ports)

    return {
        "host": host,
        "hostname": hostname,
        "asset_type": asset_type,
        "open_ports": open_ports,
        "banners": banners,
        "scanned_at": datetime.now().isoformat(),
    }


def infer_asset_type(open_ports: list[dict]) -> str:
    port_numbers = {p["port"] for p in open_ports}
    db_ports = {1433, 1521, 3306, 5432, 27017, 6379}
    web_ports = {80, 443, 8080, 8443}

    if port_numbers & db_ports:
        return "database"
    if port_numbers & web_ports:
        if port_numbers & {22, 3389}:
            return "server"
        return "web_service"
    if 3389 in port_numbers:
        return "windows_host"
    if 22 in port_numbers:
        return "linux_host"
    if 9100 in port_numbers or 631 in port_numbers:
        return "printer"
    if 32400 in port_numbers:
        return "media_server"
    if 554 in port_numbers:
        return "camera/media"
    return "unknown_device"


async def main():
    subnet = "192.168.0.0/24"
    if len(sys.argv) > 1:
        subnet = sys.argv[1]

    start = time.time()
    print(f"{'='*60}")
    print(f"  EA Discovery — Local Network Probe")
    print(f"  Subnet: {subnet}")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    live_hosts = await discover_hosts(subnet)

    if not live_hosts:
        print("[!] No live hosts found. Check your subnet or firewall settings.")
        return

    print(f"\n[*] Scanning {len(live_hosts)} hosts for {len(COMMON_PORTS)} common ports...\n")

    all_results = []
    for host in live_hosts:
        result = await scan_host_ports(host)
        all_results.append(result)

        if result["open_ports"]:
            print(f"\n  {result['host']} ({result['hostname']})  [{result['asset_type']}]")
            for p in result["open_ports"]:
                banner_preview = ""
                if p["port"] in result["banners"]:
                    banner_line = result["banners"][p["port"]].split("\n")[0][:60]
                    banner_preview = f"  | {banner_line}"
                print(f"    {p['port']:>5}/{p['service']:<20s}{banner_preview}")

    elapsed = time.time() - start

    total_services = sum(len(r["open_ports"]) for r in all_results)
    hosts_with_services = sum(1 for r in all_results if r["open_ports"])

    print(f"\n{'='*60}")
    print(f"  Scan complete in {elapsed:.1f}s")
    print(f"  Live hosts:           {len(live_hosts)}")
    print(f"  Hosts with services:  {hosts_with_services}")
    print(f"  Total open ports:     {total_services}")
    print(f"{'='*60}")

    output_file = "scripts/network_probe_results.json"
    with open(output_file, "w") as f:
        json.dump({
            "subnet": subnet,
            "scan_time": datetime.now().isoformat(),
            "elapsed_seconds": round(elapsed, 2),
            "summary": {
                "live_hosts": len(live_hosts),
                "hosts_with_services": hosts_with_services,
                "total_open_ports": total_services,
            },
            "hosts": all_results,
        }, f, indent=2)
    print(f"\n  Results saved to {output_file}")


if __name__ == "__main__":
    asyncio.run(main())
