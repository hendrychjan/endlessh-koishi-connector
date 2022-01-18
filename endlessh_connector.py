import select
import sys
import getopt
import threading
import json
import time
import requests
from systemd import journal
from datetime import datetime, date

def main(argv):
    # Load config and arguments
    arguments = parse_args(argv)
    config = load_config()
    service_args = {
        'api_url': config["api_url"],
        'token': arguments["token"],
        'provider': arguments["provider"],
        'collection_id': config["collection_id"],
    }

    # Start the statistics messenger thread
    x = threading.Thread(target = api_service, args = (service_args,)) 
    x.setDaemon(True)
    x.start()

    # Connect and listen to journalctl
    start_journal_listener()

def load_config():
    config_file = open("endlessh_connector.config", "r")
    loaded_config = {}
    for r in config_file:
        if r[0] != "#" and len(r) > 1:
            key = r.split("=")[0]
            value = r.split("=")[1].replace("\n", "")
            loaded_config[key] = value
    return loaded_config

def start_journal_listener():
    j = journal.Reader()
    j.log_level(journal.LOG_INFO)
    j.add_match(_SYSTEMD_UNIT="endlessh.service")
    j.seek_tail()
    j.get_previous()

    p = select.poll()
    p.register(j, j.get_events())
    global records
    records = []

    while p.poll():
        if j.process() != journal.APPEND:
            continue

        for entry in j:
            if entry['MESSAGE'] != "":
                if "CLOSE" in entry['MESSAGE']:
                    print("INFO: session closed")
                    log = entry['MESSAGE']
                    # Get IP
                    host_index = log.find("ffff:")
                    port_index = log.find(" port")
                    host = log[host_index + 5:port_index]

                    # Get the session length
                    time_index = log.find("time")
                    time_not_parsed = log[time_index + 5:]
                    time = time_not_parsed[:time_not_parsed.find(".")]
                    
                    new_record = [
                        {
                            "column": "Date",
                            "data": str(date.today()),
                        },
                        {
                            "column": "Time",
                            "data": datetime.now().strftime("%H:%M:%S"),
                        },
                        {
                            "column": "Duration",
                            "data": time,
                        },
                        {
                            "column": "IP",
                            "data": host,
                        }
                    ]
                    records.append(new_record)

def api_service(args):
    time.sleep(10)
    print("INFO: Sending statistics")
    api_url = args["api_url"]
    api_headers = {
        "x-auth-token": args["token"],
    }
    do_submit = True

    # Perform additional API availability check if using Koishi
    if args["provider"] == "koishi":
        status = requests.get(str(api_url + "/ping"))
        if status.status_code != 200:
            print("ERROR: API is not available")
            do_submit = False
    
    # Submit the statistics to API
    if do_submit:
        # If using Koishi, generate the collections endpoint route
        api_url = api_url + "/collections/" + args["collection_id"] + "/data"
        global records
        payload = records
        records = []
        call_failed = False
        call_error = ""
        for record in payload:
            print(record)
            res = requests.post(api_url, json = record, headers = api_headers)
            if res.status_code not in range(200, 210):
                call_failed = True
                call_error = res.text
        
        if call_failed:
            print("ERROR: " + call_error)

    # Start next worker
    x = threading.Thread(target = api_service, args = (args,))
    x.setDaemon(True)
    x.start()

def parse_args(argv):
    token = ""
    provider = ""

    try:
        opts, args = getopt.getopt(argv, "ht:p:", ["token="])
    except getopt.GetoptError:
        print("connector.py -t <api token> -p <api provider>")
        sys.exit(2)
    
    for opt, arg in opts:
        if opt == "-h":    
            print("connector.py -t <api token> -p <api provider>")
            sys.exit()
        elif opt in ("-t", "--token"):
            token = arg
        elif opt in ("-p", "--provider"):
            provider = arg

    if token == "":
        print("ERROR: Please supply token via options (-t flag)")
        sys.exit()
    if provider == "":
        print("ERROR: Please supply collection id via options (-c flag)")
        sys.exit()
    if provider not in ["koishi", "own"]:
        print("ERROR: 'Provider' can be either \"koishi\" or \"own\"")
        sys.exit()

    parsed = {
        "token": token,
        "provider": provider,
    }

    return parsed

if __name__ == "__main__":
    main(sys.argv[1:])
