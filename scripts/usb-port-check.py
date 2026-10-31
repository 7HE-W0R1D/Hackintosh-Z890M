#!/usr/bin/env python3
"""Interactive USB port checker for this Hackintosh.

Plug a device into a port and see which mapped port macOS puts it on, or
whether the port is not in the USB map (UTBMap) at all.

    python3 usb-port-check.py           interactive test, one port at a time
    python3 usb-port-check.py --list    list mapped ports and what is on them
"""
import plistlib
import subprocess
import sys
import time

CONNECTOR = {0: "USB-A 2.0", 3: "USB-A 3.x", 8: "USB-C (no switch)", 9: "USB-C",
             10: "USB-C", 255: "internal header/onboard"}
SPEED = {0: "low speed (1.5 Mb/s)", 1: "full speed (12 Mb/s)", 2: "high speed (480 Mb/s)",
         3: "SuperSpeed (5 Gb/s)", 4: "SuperSpeed+ (10 Gb/s)"}
KNOWN = {(0x0A12, 0x0001): "CSR8510 Bluetooth dongle (TP-Link UB400)",
         (0x0BDA, 0x8922): "Realtek RTL8922AE Bluetooth (onboard)"}
WAIT = 15


def ioreg_plist(*args):
    out = subprocess.run(["ioreg", "-a", "-l", "-w0", *args], capture_output=True).stdout
    return plistlib.loads(out) if out else None


def walk(node):
    yield node
    for child in node.get("IORegistryEntryChildren", []):
        yield from walk(child)


def ports():
    """Mapped controller ports (HSxx/SSxx...) by locationID."""
    roots = ioreg_plist("-r", "-c", "AppleUSBHostPort", "-d", "1") or []
    res = {}
    for p in roots if isinstance(roots, list) else [roots]:
        name = p.get("IORegistryEntryName", "?")
        loc = p.get("locationID")
        if loc is not None and name[:2] in ("HS", "SS", "US", "PR") and loc & 0x000FFFFF == 0:
            res[loc] = {"name": name, "conn": p.get("UsbConnector")}
    return res


def devices():
    """All USB devices by locationID."""
    tree = ioreg_plist("-p", "IOUSB")
    res = {}
    if not tree:
        return res
    for n in walk(tree):
        if n.get("IOObjectClass") in ("IOUSBHostDevice", "IOUSBDevice") and "locationID" in n:
            res[n["locationID"]] = n
    return res


def root_port(loc, port_map):
    """The controller port a device hangs off: same controller, first hub tier only."""
    top = loc & 0xFFF00000
    return port_map.get(top)


def describe(loc, dev, port_map):
    vid, pid = dev.get("idVendor", 0), dev.get("idProduct", 0)
    name = dev.get("USB Product Name") or dev.get("kUSBProductString") or dev.get("IORegistryEntryName", "?")
    print(f"\n  Device : {name}  ({vid:04x}:{pid:04x})")
    if (vid, pid) in KNOWN:
        print(f"           -> {KNOWN[(vid, pid)]}")
    if dev.get("bDeviceClass") == 0xE0:
        print("           -> USB device class 0xE0 = Bluetooth controller")
    speed = dev.get("Device Speed", dev.get("USBSpeed"))
    if speed is not None:
        print(f"  Speed  : {SPEED.get(speed, speed)}")
    p = root_port(loc, port_map)
    behind_hub = loc & 0x000FFFFF != 0
    if p:
        conn = CONNECTOR.get(p["conn"], p["conn"])
        where = f"{p['name']} ({conn})"
        print(f"  Port   : {where}" + ("  -- through a USB hub" if behind_hub else ""))
        print("  Result : OK, this port is mapped and macOS sees the device.")
    else:
        print(f"  Port   : unknown (locationID 0x{loc:08x})")


def list_ports():
    port_map, devs = ports(), devices()
    print("Mapped ports (what macOS can use):")
    for loc in sorted(port_map):
        p = port_map[loc]
        on = [d.get("USB Product Name") or d.get("IORegistryEntryName", "?")
              for l, d in devs.items() if l == loc]
        print(f"  {p['name']:6} {CONNECTOR.get(p['conn'], p['conn']):24} -> {', '.join(on) or '(empty)'}")


def interactive():
    print("USB port checker. Ctrl+C to quit.\n")
    print("Any USB device works for testing a port (the UB400, a flash drive...).")
    print("A USB 2.0 device like the UB400 always shows on an HSxx port, even in a blue USB 3 socket.\n")
    while True:
        input("1) Unplug the device you are testing, then press Enter... ")
        before = devices()
        port_map = ports()
        print(f"2) Now plug it into the port you want to test (waiting {WAIT} s)...", end="", flush=True)
        new = {}
        deadline = time.time() + WAIT
        while time.time() < deadline and not new:
            time.sleep(0.5)
            print(".", end="", flush=True)
            now = devices()
            new = {l: d for l, d in now.items() if l not in before}
        print()
        if new:
            # report the device closest to the root (a hub plus its children shows up together)
            for loc in sorted(new, key=lambda l: (bin(l & 0x000FFFFF).count("1"), l))[:1]:
                describe(loc, new[loc], port_map)
        else:
            print("\n  Nothing appeared.")
            print("  Result : this port is probably NOT in your USB map, so macOS can't see it.")
            print("           (Or the device needs more time / is faulty: try it in a known-good port.)")
        again = input("\nTest another port? [Y/n] ").strip().lower()
        if again.startswith("n"):
            break
        print()


if __name__ == "__main__":
    try:
        if "--list" in sys.argv:
            list_ports()
        else:
            interactive()
    except KeyboardInterrupt:
        print("\nBye.")
