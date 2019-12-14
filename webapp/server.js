var express = require('express');
var app = express();

app.use('/public', express.static(__dirname + '/public/'));
app.use('/static', express.static(__dirname + '/node_modules/'));
app.use('/app', express.static(__dirname + '/src/'));

app.get('/', function (req, res) {
   res.sendFile( __dirname + "/src/html/" + "index.htm" );
})

var server = app.listen(8081, function () {
   var host = server.address().address
   var port = server.address().port

   console.log("started server on %s:%s", host, port)
})
