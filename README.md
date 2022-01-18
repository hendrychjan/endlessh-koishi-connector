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
Create a systemd service file:
```bash
sudo nano /etc/systemd/system/endlessh-connector.service
```
And paste the following: (dont forget to replace stuff inside <>)
```bash
[Unit]
Description=Endlessh log connector
After=multi-user.target

[Service]
User=<user running endlessh>
Type=simple
Restart=always
WorkingDirectory=<path to connector - example: /opt/endlessh/endlessh-koishi-connector>
ExecStart=/usr/bin/python3 /<path to connector>/endlessh_connector.py -t <token> -p <provider>

[Install]
WantedBy=multi-user.target
```
__token__ - this will be set as a value of "x-auth-token" - if you use your own API and you do not perform any token authentication, just put in whatever, it wont be used (like "token" or something, just dont leave it empty)

__provider__ - either "koishi" or "own"

#### Additional config for Koishi
To get your auth token for Koishi-api, use the following command:
```bash
curl --location --request POST 'https://koishi-api.herokuapp.com/auth' \
--header 'Content-Type: application/json' \
--data-raw '{
    "email": "<your email>",
    "password": "<your password>"
}'
```
Also, note that the database structure should be exactly following:
```JSON
[
    {
        "columnName": "Date",
        "dataType": "date"
    },
    {
        "columnName": "Time",
        "dataType": "time"
    },
    {
        "columnName": "Duration",
        "dataType": "number"
    },
    {
        "columnName": "IP",
        "dataType": "text"
    }
]
```

### Start and enable the service
Reload systemd:
```bash
sudo systemctl daemon-reload
```

Control the systemd service:
```bash
# Start the service
sudo systemctl start endlessh-connector

# Enable the service (make it run automatically after the OS starts)
sudo systemctl enable endlessh-connector

# Check the status
sudo systemctl status endlessh-connector
```
## Finish
That should be it - statistics will submit every 3 hours.
