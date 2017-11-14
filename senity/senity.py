import uiWebServer
import simulation.simulationManager as sim
import emulation.emulationManager as emu

import console
import socket
import argparse
import multiprocessing
import ConfigParser
import sys

# Parse command line arguments
def parseArguments ():

    parser = argparse.ArgumentParser("senity")
    parser.add_argument('-c', nargs=1, help="The configuration file")
    parser.add_argument('-s', nargs=1, help="The emulation/simulation scenario file")
    parser.add_argument('-simulation', action='store_true')
    parser.set_defaults(simulation=False)
    args = parser.parse_args()

    try:
        return args.c[0], args.s[0], args.simulation
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
    enable_ui = int(config.get('Web', 'enable_ui'))
    web_port = int(config.get('Web', 'web_port'))
    base_dir = config.get('Web', 'base_dir')

    console_cmd_waiting = config.get('Console', 'console_cmd_waiting')
    if not console_cmd_waiting.isdigit():
        print("Error in configuration file: " + conf_file)
        sys.exit(0)
    else:
        console_cmd_waiting = int(console_cmd_waiting)

    return devices_folder, sites_folder, mqtt_broker_ip, mqtt_broker_port, websocket_broker_port, log_file, console_cmd_waiting, enable_ui, web_port, base_dir

if __name__ == "__main__" and __package__ is None:
    __package__ = "senity"

    # Read input parameters
    (conf_file, scenario_file, simScenario) = parseArguments()

    # Read configuration
    devices_folder, sites_folder, mqtt_broker_ip, mqtt_broker_port, websocket_broker_port, log_file, console_cmd_waiting, enable_ui, web_port, base_dir = readConfiguration(conf_file)

    if (simScenario) :
        # Start simulation Manager
        simManager = sim.simulationManager()
        simManager.start(scenario_file, devices_folder, sites_folder, mqtt_broker_ip, mqtt_broker_port, websocket_broker_port, log_file)    

    else :
        # Start emulation Manager
        emulManager = emu.emulationManager()
        emulManager.start(scenario_file, devices_folder, sites_folder, mqtt_broker_ip, mqtt_broker_port, websocket_broker_port, log_file)    

        # Start web ui
        if (enable_ui == 1):
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
