# Hackintosh-Z890M
Hackintosh file for my Intel Arrow Lake build.

## Device Information

| Parts       | Variant                        |
| ----------- | ------------------------------ |
| CPU         | Intel Core Ultra 265K 20 Core 20 Threads          |
| iGPU        | (Disabled) 4 Core Intel Xe     |
| dGPU        | Asus Dual RX 6600XT            |
| MotherBoard | [Z890M AORUS ELITE WIFI7 ICE](https://www.gigabyte.com/Motherboard/Z890M-AORUS-ELITE-WIFI7-ICE/sp) |
| WiFi / BT   | (Not working) Realtek® Wi-Fi 7 RTL8922AE |
| USB BT      | TP-Link UB-400 at red USB3.2 port in the back |
| Nvme        | Samsung 9100 Pro 1TB           |
| RAM         | 4800Mhz DDR5 16G x 2           |
| MacOS       | 15.7                           |
| OpenCore    | 1.0.6                          |

## Notable Changes
Need to manually place OpenCore USB to the first in boot order, so installation can complete.

Have to disable ~2/5 of all the backpanel USB ports to keep the 15 port limit.

Bluetooth working by using a TP-Link UB400 in any of the enabled USB port. Make sure to use `BlueToolFixup.kext` and set the two NVRAM variables mentioned in [their repo](https://github.com/acidanthera/BrcmPatchRAM?tab=readme-ov-file#bluetoolfixupkext).

Fix initially found in [reddit](https://www.reddit.com/r/hackintosh/comments/1fsvhsj/finally_i_made_my_bluetooth_work_in_sequoia/)
