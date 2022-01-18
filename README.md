# Endlessh-Koishi connector
Send Endlessh session logs to a REST API in a standardized JSON format.

Connect to Koishi and watch script kiddies get stuck.

> You can either send the data to Koishi graphs, or to your own REST API

## Installation

### Prerequisites
- Python3
- [Endlessh](https://github.com/skeeto/endlessh) installed
- sudo privileges

### Install dependencies
Install the dependencies listed below using the package manager of your choice.
```bash
sudo apt install libsystemd0 libsystemd-dev python3-systemd
```

### Alter user permissions
Make sure the user running endlessh-koishi connector can access journals of Endlessh. If it is a regular user with `sudo` privileges, add that user to usergroup `systemd-journal`

```bash
# Replace "your_user" with the name of your user
sudo usermod -a -G systemd-journal your_user
```

You can test it with:
```bash
# Replace "unit_name" with the name of systemd unit that is running Endlessh 
# (endlessh.service most likely)
journalctl --unit unit_name
```

### Install and setup endlessh-koishi connector
First, clone [this](https://github.com/hendrychjan/endlessh-koishi-connector) repository and `cd` in there
```bash
git clone https://github.com/hendrychjan/endlessh-koishi-connector.git
cd endlessh-koishi-connector
```

Then, edit the `endlessh_connector.config` file accordingly. It could look something like this:
```text
# This is an example endlessh-koishi connector config file

# Name of the unit that Endlessh is running under
service_name=endlessh.service

# Could be either the official Koishi API url, or your own API
api_url=https://koishi-api.herokuapp.com

# In case you are using Koishi, make sure you supply _id of the collection
# that collects the session info statistics
collection_id=61dedbebdb77a16b69ba5d4a
```

### Run connector as a systemd unit
#### Using your own API
Create a systemd service file:
```bash
sudo nano /etc/systemd/system/test.service
```
And paste the following: (dont forget to replace stuff inside <>
```bash
[Unit]
Description=Endlessh log connector
After=multi-user.target

[Service]
User=<user running endlessh>
Type=simple
Restart=always
ExecStart=/usr/bin/python3 /<path to connector>/endlessh_connector.py -t <user token> -p <provider>

[Install]
WantedBy=multi-user.target
```
__user token__ - if you are using Koishi, you need to supply the _x-auth-token_ to authenticate yourself

__provider__ - could be either "koishi" or "own"
