<div align="center">
  <img src="data/icons/hicolor/scalable/apps/io.github.lo2dev.Echo.svg" width="128" height="128">

  # Echo

  Ping websites

  <img src="data/screenshots/1.png">
</div>


## The Project

Echo is a simple utility to ping websites using GTK4 and Libadwaita.

## Features

Besides doing the default ping, you can configure the:
- Number of pings
- Interval between each packet
- Timeout
- And more

## Installation
<a href='https://flathub.org/apps/io.github.lo2dev.Echo'><img width='240' alt='Get it on Flathub' src='https://flathub.org/api/badge?locale=en'/></a>

## Insufficient permissions?
Unfortunetly, on some systems, the feature needed to ping is not available by default so you have to do a manual setup.

This will require running terminal commands:

```sh
echo 'net.ipv4.ping_group_range = 0 2147483647' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

## Planned
- Ping history
- Stop ping midway

## Code of Conduct

The project follows the [GNOME Code of Conduct](https://conduct.gnome.org/).
