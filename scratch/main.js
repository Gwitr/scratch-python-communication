var net = require("net");
var Scratch = require('scratch-api');

var current_listener = null;

var srv = net.createServer();

var PROJ_ID = 317357163
var tmout   = false;

srv.listen(8080, function() {
	console.log("Logging in to scratch...");
	Scratch.UserSession.load(function(err, user) {
		console.error("Done loading.");
		srv.on("connection", function(c) {
			current_listener = c;
			user.cloudSession(PROJ_ID, function(err, cloud) {
				cloud.on("error", function(err) {
					console.log("cloud", err);
					current_listener = null;
				});
				c.on("end", function() {
					current_listener = null;
					cloud.end();
				});
				srv.on("error", function(err) {
					console.log(err);
					current_listener = null;
					cloud.end();
				});
				console.log("Obtained a cloud session.");
				current_listener.on("data", function(d) {
					// ☁☁☁☁☁☁
					d = d.toString("latin1");
					console.log(d);
					if (d.substr(0, 4) === "set\\") {
						var i = 4
						var name = ""
						while (1) {
							if (name[name.length - 1] === "\\") {
								break
							}
							name += d[i];
							i += 1;
						}
						var value = d.substr(i);
						console.log("☁ " + name.substr(0, name.length - 1), value);
						cloud.set("☁ " + name.substr(0, name.length - 1), value);
					} else if (d.substr(0, 4) === "get\\") {
						var name = d.substr(4);
						var val  = cloud.get("☁ " + name);
						console.log("get(", name, ", ", val, ")");
						current_listener.write("set" + "\\" + name + "\\" + val + "\\");
					}
				});
				cloud.on('set', function(name, value) {
					console.log(name, value);
					if (current_listener !== null) {
						if (tmout !== true)  current_listener.write("set" + "\\" + name.substr(2) + "\\" + value + "\\");
					}
				});
				setTimeout(function(){tmout=true}, 5000);
			});
		});
	});
});