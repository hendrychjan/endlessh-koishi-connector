def load_config():
    config_file = open("endlessh_connector.config", "r")
    loaded_config = {}
    for r in config_file:
        if r[0] != "#" and len(r) > 1:
            key = r.split("=")[0]
            value = r.split("=")[1].replace("\n", "")
            loaded_config[key] = value
    return loaded_config

print(load_config())