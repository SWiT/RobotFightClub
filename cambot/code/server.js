var doT = require('dot');

var express = require('express');
var app = express();
app.use(express.urlencoded());

var server = require('http').createServer(app);
var io = require('socket.io').listen(server);

var b = require('bonescript');
var os = require('os');
var spawn = require('child_process').spawn;

var webport = 81;
var socketport = 1080;
var streamport = 8080;

server.listen(socketport);

var appLocation = "/var/lib/cloud9/cambot";
var cameraCommandPath = '/home/root/mjpg-streamer-code/mjpg-streamer-experimental';
var wificonfig = '/var/lib/connman/wifi.config';
var pagetitle = "BeagleBone Black Webcam Stream";

var wifi_ssid = '';
var wifi_security = '';
var wifi_passphrase = '';

var cameraOn = false;
var mjpg_streamer;

var button_fwd = false;
var button_rev = false;
var button_left = false;
var button_right = false;

var leftServo = 'P9_14';
var rightServo = 'P9_22';

var bumpSwitchLeft = 'P9_16';
var bumpSwitchRight = 'P9_18';

/****************************
 * Setup
 */
var osni = os.networkInterfaces();
console.log("server running at:");

var ipaddress = osni.lo[0].address;
console.log(" http://%s:%s", ipaddress, webport);
if(osni.usb0){
    var ipaddress = osni.usb0[0].address;
    console.log(" http://%s:%s", ipaddress, webport);
}
if(osni.wlan0){
    ipaddress = osni.wlan0[0].address;
    console.log(" http://%s:%s", ipaddress, webport);
}
if(osni.eth0){
    ipaddress = osni.eth0[0].address;
    console.log(" http://%s:%s", ipaddress, webport);
}



/***********************************
 * Servo stuff
 */

b.pinMode(leftServo, b.OUTPUT);
b.pinMode(rightServo, b.OUTPUT);
var leftServoValue = 0; //-100 to 100
var rightServoValue = 0; //-100 to 100
var updateServos = function() {
    var ccw = 1.7;  //counter clockwise timing in ms
    var stop = 1.5; //stop position timing in ms
    var cw = 1.3;   //clockwise timing in ms
    var pause = 20; //time to pause after a pulse in ms
    var pulse;
    if(leftServoValue >= 0){
        pulse = stop + ((ccw - stop)*(leftServoValue/100));
    }else{
        pulse = stop + ((cw - stop)*(-leftServoValue/100));
    }
    var duty = pulse/(pulse + pause); 
    var freq = 1000/(pulse + pause);
    b.analogWrite(leftServo, duty, freq);
    
    if(rightServoValue >= 0){
        pulse = stop + ((cw - stop)*(rightServoValue/100));
    }else{
        pulse = stop + ((ccw - stop)*(-rightServoValue/100));
    }
    duty = pulse/(pulse + pause); 
    freq = 1000/(pulse + pause);
    b.analogWrite(rightServo, duty, freq);
};
updateServos();




/****************************
 * Resources
 */

app.get('/', function(req, res){
    startCamera();
    logRequest(req);
    
    var hostname = req.headers.host.split(":")[0];
    
    //Get wifi config settings
    parsewificonfig(b.readTextFile(wificonfig));
    
    var body = '';
    body += '<script src="http://yui.yahooapis.com/3.14.1/build/yui/yui-min.js"></script>';
    body += '<script src="http://'+hostname+':'+socketport+'/socket.io/socket.io.js"></script>';
    body += '<input id="socketiohost" type="hidden" value="'+hostname+':'+socketport+'" />';
    body += '<script type="text/javascript" src="client.js"></script>';
    body += '<link rel="stylesheet" type="text/css" href="default.css">';
    body += '<h1>'+pagetitle+'</h1>\n';
    body += '<div id="videostreamcontainer" class="container"><img id="videostream" src="http://'+hostname+':'+streamport+'/?action=stream" /></div>\n';
    
    body += '<div class="container control-pad">';
    body += '<div id="arrow-up" class="arrow-up"></div>';
    body += '<div id="arrow-down" class="arrow-down"></div>';
    body += '<div id="arrow-left" class="arrow-left"></div>';
    body += '<div id="arrow-right" class="arrow-right"></div>';
    body += '</div>';
    
    var tempFn = doT.template(b.readTextFile(appLocation+'/form_wifi.html'));
    body += tempFn({wifi_ssid:wifi_ssid, wifi_security:wifi_security, wifi_passphrase:wifi_passphrase});
    
    res.send(body);
    res.end();
});

app.get('/client.js', function(req, res){
    logRequest(req);
    res.send(b.readTextFile(appLocation+req.url));
});

app.get('/default.css', function(req, res){
    logRequest(req);
    res.send(b.readTextFile(appLocation+req.url));
});


/******************************************************
 * Websocket commands
 */

io.sockets.on('connection', function(socket) {
  //socket.emit('robotstatus', { servoL:'?',servoR:'?','bumpL':0,'bumpR':0 });
  
  socket.on('disconnect', function() {
    console.log('socket:client disconnected');
    stopMotors();
    stopCamera();
  });
  
  socket.on('drive', function(data) {
    clearTimeout(motortimerid);
    if(data.status=='down'){
        switch(data.key){
            case 'up-arrow':
                button_fwd = true;
                break;
            case 'down-arrow':
                button_rev = true;
                break;
            case 'left-arrow':
                button_left = true;
                break;
            case 'right-arrow':
                button_right = true;
                break;
        }
    }else if(data.status=='up'){
        switch(data.key){
            case 'up-arrow':
                button_fwd = false;
                break;
            case 'down-arrow':
                button_rev = false;
                break;
            case 'left-arrow':
                button_left = false;
                break;
            case 'right-arrow':
                button_right = false;
                break;
        }
    }
    setMotors();
  });
  
});



/******************************************************
 * Post Commands
 */

app.post('/updatewifi', function(req, res){
    logRequest(req);
    
    wifi_ssid = req.body.wifi_ssid;
    wifi_security = req.body.wifi_security;
    wifi_passphrase = req.body.wifi_passphrase;
    
    var configdata = "[service_home]\n";
    configdata += "Type = wifi\n";
    configdata += "Name = "+wifi_ssid+"\n";
    if (wifi_security !== ''){
        configdata += "Security = "+wifi_security+"\n";
    }
    if (wifi_passphrase !== ''){
        configdata += "Passphrase = "+wifi_passphrase+"\n";
    }
    b.writeTextFile(wificonfig, configdata);
    res.send('Updated WiFi configuration.  Restarting now.<br/>Wait a while then go <a href="/">back</a>');
    spawn('reboot');
});

app.get('/poweroff', function(req, res){
    logRequest(req);
    res.send('Shutting down now.');
    res.end();
    spawn('poweroff');
});

app.get('/reboot', function(req, res){
    logRequest(req);
    res.send('Restarting now.<br/>Wait a while then go <a href="/">back</a>');
    res.end();
    spawn('reboot');
});

app.listen(webport);


/**************************************************
 * Functions
 */
var stopMotors = function(){
    button_fwd = false;
    button_rev = false;
    button_left = false;
    button_right = false;
    setMotors();
}; 

var motortimerid;
var expireMotors = function(){
    console.log(printDateTime() + ' waiting...');
    stopMotors();
};

var setMotors = function (){
    var speed = 20;
    if((button_fwd && button_rev) || (button_left && button_right)){    //WTF are you doing?  Damn button masher.
        console.log(printDateTime() + ' drive: WTF');
        rightServoValue = 0;
        leftServoValue = 0;
    }else if(button_fwd){
        if(button_left){        //Forward Left
            console.log(printDateTime() + ' drive: Forward Left');
            rightServoValue = speed;
            leftServoValue = speed/2;
        }else if(button_right){ //Forward Right
            console.log(printDateTime() + ' drive: Forward Right');
            rightServoValue = speed/2;
            leftServoValue = speed;
        }else{                  //Forward
            console.log(printDateTime() + ' drive: Forward');
            rightServoValue = speed;
            leftServoValue = speed;
        }
    }else if(button_rev){
        if(button_left){        //Reverse Left
            console.log(printDateTime() + ' drive: Reverse Left');
            rightServoValue = -speed;
            leftServoValue = -speed/2;
        }else if(button_right){ //Reverse Right
            console.log(printDateTime() + '  drive: Reverse Right');
            rightServoValue = -speed/2;
            leftServoValue = -speed;
        }else{                  //Reverse
            console.log(printDateTime() + ' drive: Reverse');
            rightServoValue = -speed;
            leftServoValue = -speed;
        }
    }else if(button_left){      //Rotate Left
        console.log(printDateTime() + ' drive: Rotate Left');
        rightServoValue = speed;
        leftServoValue = -speed;
    }else if(button_right){     //Rotate Right
        console.log(printDateTime() + ' drive: Rotate Right');
        rightServoValue = -speed;
        leftServoValue = speed;
    }else{
        console.log(printDateTime() + ' drive: Stop');
        rightServoValue = 0;
        leftServoValue = 0;
    }
    updateServos();
    
    if(motortimerid){clearTimeout(motortimerid);}
    motortimerid = setTimeout(expireMotors, 3000);
};

var parsewificonfig = function(data){
    var lines = data.split("\n");
    for (var key in lines){
        var line = lines[key].trim();
        if(line.substr(0,1) == "#"){
            continue;
        }else if(line.substr(0,1) == "["){
            continue;
        }else if(line.substr(0,4) == "Type"){
            continue;
        }else if(line.substr(0,4) == "Name"){
            wifi_ssid = line.substr(7);
        }else if(line.substr(0,8) == "Security"){
            wifi_security = line.substr(11);
        }else if(line.substr(0,10) == "Passphrase"){
            wifi_passphrase = line.substr(13);
        }
    }
};

var startCamera = function(){
    if(!cameraOn){
        console.log(printDateTime()+" starting camera.");
        mjpg_streamer = spawn(cameraCommandPath+'/mjpg_streamer', ['-i',cameraCommandPath+'/input_uvc.so','-o',cameraCommandPath+'/output_http.so'], {cwd:cameraCommandPath});
        /*mjpg_streamer.stdout.on('data', function (data) {
          console.log('stdout: ' + data);
        });    
        mjpg_streamer.stderr.on('data', function (data) {
          console.log('stderr: ' + data);
        });
        mjpg_streamer.on('exit', function (code) {
          console.log('child process exited with code ' + code);
        });*/
        cameraOn = true;
    }
};

var stopCamera = function(){
    console.log( printDateTime()+" stopping camera.");
    cameraOn = false;
    if(mjpg_streamer){
        mjpg_streamer.kill();
    }
};

var printDateTime = function(){
    var now = new Date();
    var datetime = now.getFullYear()+"-"+(now.getMonth()+1)+"-"+now.getDate()+" ";
    datetime += now.getHours()+":"+("0"+now.getMinutes()).substr(-2,2)+":"+("0"+now.getSeconds()).substr(-2,2);
    return datetime;
};

var logRequest = function(req){
    var log = "";
    log += printDateTime();
    log += " "+req.headers.host+req.url;  //Requested URL
    log += " "+req.connection.remoteAddress;    //users IP address.
    console.log(log);
};


