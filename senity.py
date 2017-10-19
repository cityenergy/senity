import emulationManager
import uiWebServer

import console
import socket
import argparse
import multiprocessing
import ConfigParser

# Parse command line arguments
def parseArguments ():

    parser = argparse.ArgumentParser("senity")
    parser.add_argument('-c', nargs=1, help="The configuration file")
    parser.add_argument('-s', nargs=1, help="The emulation scenario file")
    args = parser.parse_args()

    try:
        return args.c[0], args.s[0]
    except Exception:
        parser.print_help()
        sys.exit(0)

# Read configuration parameters
def readConfiguration (conf_file):

    config = ConfigParser.ConfigParser()
    try:
        config.read(conf_file)
    except Exception:
        print("Could not read configuration file: " + conf_file)
        sys.exit(0)

    devices_folder = config.get('General', 'devices_folder')
    sites_folder = config.get('General', 'sites_folder')
    mqtt_broker_ip =  config.get('General', 'mqtt_broker_ip')
    mqtt_broker_port = config.get('General', 'mqtt_broker_port')
    websocket_broker_port = config.get('General', 'websocket_broker_port')
    log_file = config.get('General', 'log_file')
    enable_ui = bool(config.get('Web', 'enable_ui'))
    web_port = int(config.get('Web', 'web_port'))
    base_dir = config.get('Web', 'base_dir')

    console_cmd_waiting = config.get('Console', 'console_cmd_waiting')
    if not console_cmd_waiting.isdigit():
        print("Error in configuration file: " + conf_file)
        sys.exit(0)
    else:
        console_cmd_waiting = int(console_cmd_waiting)

    return devices_folder, sites_folder, mqtt_broker_ip, mqtt_broker_port, websocket_broker_port, log_file, console_cmd_waiting, enable_ui, web_port, base_dir

if __name__ == "__main__":

    # Read input parameters
    (conf_file, scenario_file) = parseArguments()

    # Read configuration
    devices_folder, sites_folder, mqtt_broker_ip, mqtt_broker_port, websocket_broker_port, log_file, console_cmd_waiting, enable_ui, web_port, base_dir = readConfiguration(conf_file)

    # Start emulation Manager
    emulManager = emulationManager.emulationManager()
    emulManager.start(scenario_file, devices_folder, sites_folder, mqtt_broker_ip, mqtt_broker_port, websocket_broker_port, log_file)    

    # Start web ui
    if (enable_ui):
        uiWeb = uiWebServer.uiWebServer(web_port, base_dir)
        sp = multiprocessing.Process(target= uiWeb.start, args=())
        sp.start()

    # Start interactive console
    senityConsole = console.console(mqtt_broker_ip, mqtt_broker_port, console_cmd_waiting)
    senityConsole.start()	

    # Close emulation manager
    emulManager.closeSenity()
    if (enable_ui):
        sp.terminate()
