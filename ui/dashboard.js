var sitesConsumptionArray = new Array();
var sitesCountDevicesOn = new Array();
var sitesCount = new Array();

$(document).ready(function() {

    // Create main chart
    initCityConsumptionChart("totalCityConsumptionChart", "totalCityConsumptionValue");
    createCityConsumptionChart("totalCityConsumptionChart", "totalCityConsumptionValue", moment().subtract(100 * 1000, 'ms'), moment());

    // Connect, subscribe, handle msgs to/from mqtt broker
    mqttSetup();
    
});

// Connect, subscribe, handle msgs to/from mqtt broker
function mqttSetup () {

    var client = new Paho.MQTT.Client("127.0.0.1", 9001, "myclientid_" + parseInt(Math.random() * 100, 10));
    var clientConnected = false;

    // Gets  called if the websocket/mqtt connection gets disconnected for any reason
    client.onConnectionLost = function(responseObject) {
        //Depending on your scenario you could implement a reconnect logic here
        clientConnected = false;
    };

    //Gets called whenever you receive a message for your subscriptions
    client.onMessageArrived = function(message) {
        //console.log(message.destinationName + ' - ' + message.payloadString);
        if ((message.destinationName).indexOf("site_conf") >= 0) {
            msgSplit = (message.destinationName).split('/');
            if (message.payloadString == "") { 
                // A small hack based on the way senity works, "deregistring" retained values in mqqt, on exit. Do not tell anyone :)
                sitesCount[msgSplit[1]] = 0;
            } else {
                sitesCount[msgSplit[1]] = 1;
            }
            $('#numberOfSites').text(sitesCount.reduce(getSum));

            if (sitesCount.reduce(getSum) == 0) {
                document.getElementById('totalCityConsumptionValue').value = 0;
            }

        } else if ((message.destinationName).indexOf("site_consumption") >= 0) {
            msgSplit = (message.destinationName).split('/');
            sitesConsumptionArray[msgSplit[1]] = parseInt(message.payloadString);
            document.getElementById('totalCityConsumptionValue').value = sitesConsumptionArray.reduce(getSum)/1000;
        } else if ((message.destinationName).indexOf("site_devices_conf") >= 0) {
            msgSplit = (message.destinationName).split('/');
            // A small hack based on the way senity provides information regarding the configurations of sites.
            sitesCountDevicesOn[msgSplit[1]] = ((message.payloadString).match(/\'status\': 1/g) || []).length;   
            $('#numberOfAppliances').text(sitesCountDevicesOn.reduce(getSum));
        }    
     };

     //Connect Options
     var options = {
         timeout: 3,
         //Gets Called if the connection has sucessfully been established
         onSuccess: function() {
             //console.log("Connected");
             clientConnected = true;
             client.subscribe("site_conf/#", {qos: 0})
             client.subscribe("site_consumption/#", {qos: 0})
             client.subscribe("site_devices_conf/#"), {qos: 0}
         },
         //Gets Called if the connection could not be established
         onFailure: function(message) {
             //console.log("Connection failed: " + message.errorMessage);
         }
     };

     client.connect(options)
     
}

// Initialize main chart
function initCityConsumptionChart(divId, variableName) {

    var chart = $('#' + divId + '').highcharts({
        chart: {
            backgroundColor: null,
            width: '600',
            height: '400',
            style : {
                color: "#0f335f"
            }
         },
         
        title: {
            text: 'Real Time Consumption (KWatts) for all sites',
            style : {
                color: "#0f335f"
            }
        },
        xAxis: {
            type: 'datetime',
            tickPixelInterval: 150,
            minorTickInterval: 'auto',
            minorTickLength: 0
        },
        yAxis: {
            minorTickInterval: 'auto',
            minorTickLength: 0,
            title: {
                text: "KWatts"
            }
        },
        credits: {
            enabled: false
        },
        legend: {
            enabled: false
        },
        plotOptions: {
            spline: {
                lineWidth: 2,
                states: {
                    hover: {
                        lineWidth: 3
                    }
                },
                marker: {
                    enabled: false
                }
            }
        },
        series: []
    });

    intervalTotalPowerLive(divId, variableName);

}

// Create main chart
function createCityConsumptionChart(divId, variableName, dateFrom, dateTo) {

    var data = [],
        time = (new Date()).getTime(),
        i;

    var val = parseFloat($("#" + variableName ).text());
    
    for (i = -19; i <= 0; i += 1) {
        data.push({
            x: time + i * 1000,
            y: parseFloat(val)
        });
    }

    //add serie to series
    var chart = $('#' + divId + '').highcharts();

    chart.addSeries({
        id: variableName,
        name: "City Consumption",
        data: data
    });
}

// Main chart interval function
function intervalTotalPowerLive(chartContainer, variableName) {
    setInterval(function() {
        var chart = $('#' + chartContainer + '').highcharts();
        var time = (new Date()).getTime();

        $(chart.series).each(function(i, serie) {
            var floatI = parseInt(document.getElementById(variableName).value);
            serie.addPoint([time, floatI]);
        })

    }, 1000);
}

// Helper function for getting a sum of the values in an array
function getSum(total, num) {
    return total + num;
}
