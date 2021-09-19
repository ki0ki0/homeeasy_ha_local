# homeeasy_ha_local
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)


[Hass.io](https://home-assistant.io/) integration for HVAC units compatible with Home Easy application

## Description

This integration uses [homeeasylib](https://github.com/ki0ki0/homeeasylib) project

Compatible with original Home Easy application:
- Android [Home Easy](https://play.google.com/store/apps/details?id=net.conditioner.web)
- iOS [Home Easy](https://itunes.apple.com/cn/app/home-easy/id1263076928?mt=8)

### List of compatible HVAC units:
- Cooper&Hunter Nordic Premium CH-S09FTXN-PW


## Installation
1. Install [HACS](https://hacs.xyz/)
2. Add THIS repository as [custom repository](https://hacs.xyz/docs/faq/custom_repositories)
3. Restart HA
4. Add new integration with UI flow: Configuration → Integrations → Add integration(bottom right corner) → Search for “Home Easy HVAC Local” → Type device IP…

## Cloud-based version
There is also a cloud-based version of this integration at [homeeasy_ha](https://github.com/ki0ki0/homeeasy_ha).

### Main differences:
- Local integration directly connects to an HVAC unit so doesn't depend on the manufacturer's cloud infrastructure and internet connection.
- Local integration provides the ability to control vertical and horizontal airflow direction.

### Security:
The manufacturer server provides unauthorized access to ANY connected HVAC unit, so anyone can read the current state and set any parameters.

It is a good idea to block access to IP 91.196.132.126 on your firewall.

This IP is part of the QR code from the user manual, but my HVAC actually ignores any IP I've provided over QR code and connects to 91.196.132.126 anyway.
It is also possible to switch the original Home Easy App to this mode, but your phone has to be connected to the same network to control the unit. Just drop app data(reinstall application) and scan any QR with simple text.

### Sample QR code("CooperHunter" text):
![qr-code](https://user-images.githubusercontent.com/1998334/133943978-1b33b0d8-a54e-44fa-9fbd-65bd01916230.gif)


## License

This project is licensed under the GNU GPLv3 - see the [LICENSE](LICENSE) file for details

## Acknowledgments

- Inspired by [cooper_hunter-hvac-mqtt-bridge](https://github.com/T-REX-XP/cooper_hunter-hvac-mqtt-bridge) project by [T-REX-XP](https://github.com/T-REX-XP)
and [Arthur Krupa](https://github.com/arthurkrupa).
