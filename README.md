## Synopsis

SENITY is an emulator for smart energy deployments targeting city environments. It can emulate sites that contain a smart energy meter, smart energy devices and appliances. Its goal is to become a mininet-like tool promoting research in the respective field, making possible to evaluate algorithms, energy models and complete energy systems (e.g. for demand/response, pricing etc), in various city scenarios.

For more informations regarding architecture, implementation, installation and usage please refer to the https://github.com/pkokkinos/senity/wiki.

## Set up
To setup the environment one needs to i) get the files, ii) install and run mosquitto mqtt broker, using the latest source and compiling/running with websocket support, iii) install necessary python libraries (e.g., paho, prompt_toolkit), iv) in the ui/dashboard.js setup the ip of your machine

## Run
To run senity simply hit:
python senity.py  -c senity.conf -s scenarios/emuScenario01.json
and you are done. A console will appear through which one is able to issue a number of commands (e.g. turning on/off devices) and also visit your_ip:8080/dashboard.html

## Contact
Panagiotis Kokkinos, kokkinop@gmail.com

