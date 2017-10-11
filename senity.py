import emulationManager
import console

import argparse

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

if __name__ == "__main__":

    # Read input parameters
    (conf_file, scenario_file) = parseArguments()

    # Start emulation Manager
    emulManager = emulationManager.emulationManager()
    emulManager.start(conf_file, scenario_file)    
    
    # Start interactive console
    (mqtt_broker_ip, mqtt_broker_port, console_cmd_waiting) = emulManager.getConfParams()    
    senityConsole = console.console(mqtt_broker_ip, mqtt_broker_port, console_cmd_waiting)
    senityConsole.start()	

    # Close emulation manager
    emulManager.closeSenity()
