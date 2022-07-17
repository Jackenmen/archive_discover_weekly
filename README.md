# archive_discover_weekly

Script that archives Spotify Discover Weekly playlist to your email.


## Requirements

- Python 3.8+
- requests library


## Installation

### Ubuntu

1. Install the requirements:
   ```
   sudo apt install python3 python3-requests git
   ```
1. Clone this repository and go into it:
   ```
   git clone https://github.com/jack1142/archive_discover_weekly
   cd archive_discover_weekly
   ```
1. Install systemd service files:
   ```
   sudo cp systemd_service_files/archive_discover_weekly.timer /etc/systemd/system
   service_contents=$(cat systemd_service_files/archive_discover_weekly.service)
   service_contents=$(echo "$service_contents" | PYTHON="$(which python3)" envsubst)
   echo "$service_contents" | sudo tee /etc/systemd/system/archive_discover_weekly.service
   ```
1. Create an `override.conf` file in `/etc/systemd/system/archive_discover_weekly.service.d/` directory
   (you will need to create it) based on the template file located at
   `systemd_service_files/archive_discover_weekly.service.d/override.conf` in this repository.
1. Enable systemd timer:
   ```
   sudo systemctl enable archive_discover_weekly.timer
   ```

### Other systemd-based Linux operating systems

1. Install Python 3.8+ and git with your system's package manager.<br>
   When using a distribution that debundles venv/ensurepip from base Python package,
   make sure to also install package providing those modules as well.
1. Clone this repository and go into it:
   ```
   git clone https://github.com/jack1142/archive_discover_weekly
   cd archive_discover_weekly
   ```
1. Create a virtual environment and install requests in it:
   ```
   cd archive_discover_weekly
   python3 -m venv .venv
   .venv/bin/python -m pip install -U requests
   ```
1. Install systemd service files:
   ```
   sudo cp systemd_service_files/archive_discover_weekly.timer /etc/systemd/system
   service_contents=$(cat systemd_service_files/archive_discover_weekly.service)
   service_contents=$(echo "$service_contents" | PYTHON="$PWD/.venv/bin/python" envsubst)
   echo "$service_contents" | sudo tee /etc/systemd/system/archive_discover_weekly.service
   ```
1. Create an `override.conf` file in `/etc/systemd/system/archive_discover_weekly.service.d/` directory
   (you will need to create it) based on the template file located at
   `systemd_service_files/archive_discover_weekly.service.d/override.conf` in this repository.
1. Enable systemd timer:
   ```
   sudo systemctl enable archive_discover_weekly.timer
   ```

### Windows & macOS

Installation instructions not available, sorry.


## License

Please see [LICENSE file](LICENSE) for details. In short, this project is open source and you are free to modify and use my work as long as you credit me.

---

> Jakub Kuczys &nbsp;&middot;&nbsp;
> GitHub [@jack1142](https://github.com/jack1142)
