# Hackintosh-Z890M
Hackintosh file for my Intel Arrow Lake build.

> This branch is the current build with an **NVIDIA RTX 4070 Super**. The previous RX 6600 XT build (Sequoia and Tahoe EFIs) is on the [`AMD-6600XT`](../../tree/AMD-6600XT) branch.

## Device Information

| Parts       | Variant                        |
| ----------- | ------------------------------ |
| CPU         | Intel Core Ultra 265K 20 Core 20 Threads          |
| iGPU        | (Disabled) 4 Core Intel Xe     |
| dGPU        | NVIDIA GeForce RTX 4070 Super 12 GB ([NullMoth](https://github.com/nullmoth/nvidia-macos-driver) driver, Metal 3) |
| MotherBoard | [Z890M AORUS ELITE WIFI7 ICE](https://www.gigabyte.com/Motherboard/Z890M-AORUS-ELITE-WIFI7-ICE/sp) |
| WiFi        | Realtek® Wi-Fi 7 RTL8922AE (onboard), working with [AirPort_RTW89](https://github.com/FranciumOS-org/Airport_RTW89) |
| USB BT      | TP-Link UB400 (CSR8510)        |
| Ethernet    | Realtek RTL8125 2.5GbE (LucyRTL8125Ethernet) |
| Nvme        | Samsung 9100 Pro 1TB           |
| RAM         | 4800Mhz DDR5 16G x 2           |
| SMBIOS      | MacPro7,1                      |
| MacOS       | 26.7.1 (25G241)                |
| OpenCore    | 1.0.6                          |

The EFI is in [`EFI-Tahoe`](EFI-Tahoe). Serial number, MLB, UUID and ROM in `config.plist` are redacted (`XXXXX`). Generate your own with [GenSMBIOS](https://github.com/corpnewt/GenSMBIOS) before booting.

## Notable Changes

### Graphics: RTX 4070 Super
- Driver: NullMoth nvidia-macos-driver 2.6.5, installed with its 1401 Mac app. The kexts live in `/Library/Extensions`, not in the EFI.
- The app sets the boot-args `nvfb=1 nvaccel=1 nvfbheads=4 -nvkmsnosmooth amfi_get_out_of_my_way=0x1 amfi=0x80 ipc_control_port_options=0`, Kernel -> Block `com.apple.iokit.IONDRVSupport`, and the `NullMothSafe.efi` tools (start once without the NVIDIA driver, or remove it).
- WhateverGreen and `agdpmod=pikera` are off (AMD only).

### Secure Boot
- Needs `SecureBootModel = Disabled`. BIOS UEFI Secure Boot stays **on** here (Windows anti-cheat), which only boots with `UEFI -> Quirks -> DisableSecurityPolicy = true`.
- With that quirk on, boot Windows from the F12 menu (Windows Boot Manager), not through OpenCore.
- `csr-active-config` = `0x0A43`, plus AMFIPass with `-amfipassbeta`.

### Wi-Fi: onboard RTL8922AE
- [AirPort_RTW89](https://github.com/FranciumOS-org/Airport_RTW89) 0.5.0-beta (driver + its `AirPortRTW89Front` plugin, both in Kernel -> Add) on the old Wi-Fi stack: Ventura's `IOSkywalkFamily` + `IO80211FamilyLegacy` from OCLP, with Kernel -> Block for the native `com.apple.iokit.IOSkywalkFamily`.
- **No root patch needed.** The system volume stays sealed.
- Also block `com.apple.driver.AppleEthernetRL`. Apple's RTL8125 driver links against the native Skywalk and stops the boot once Skywalk is swapped. LucyRTL8125Ethernet takes over wired Ethernet.
- Tested: 802.11ac, 5 GHz, 80 MHz, WPA2/WPA3 Personal. No AirDrop / AWDL.

### Bluetooth: TP-Link UB400
- `BlueToolFixup.kext` + the UB400 in any mapped USB port. No firmware kext needed.
- NVRAM (7C436110-AB2A-4BBB-A880-FE41995C9F82): `bluetoothHostControllerSwitchBehavior = always`, `bluetoothExternalDongleFailed = 00`, `bluetoothInternalControllerInfo = 0000...`. All three are also in NVRAM -> Delete, so they are rewritten at every boot. macOS sets `bluetoothExternalDongleFailed` to `01` after one failed start and then ignores the dongle.
- The onboard RTL8922AE Bluetooth (USB `0bda:8922`) does not work: macOS aborts the controller init at `SetEventMaskPage2` (STATUS 46).
- Fix initially found in [reddit](https://www.reddit.com/r/hackintosh/comments/1fsvhsj/finally_i_made_my_bluetooth_work_in_sequoia/).

### Audio
AppleALC with `alcid=11`, plus SimpleHDA.

### USB
Need to manually place OpenCore USB to the first in boot order, so installation can complete.

Have to disable ~2/5 of all the backpanel USB ports to keep the 15 port limit. [`scripts/usb-port-check.py`](scripts/usb-port-check.py) shows which mapped port a newly plugged device lands on, or that a socket is not mapped (`--list` shows all mapped ports).
