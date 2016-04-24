var sysargs = require('system').args;
console.log(sysargs[sysargs.length-1]);
workingDir = fs.absolute(sysargs[sysargs.length-1]).split('/');
workingDir.pop(); //remove filename
workingDir = workingDir.join('/');
fs.changeWorkingDirectory(workingDir);

phantom.injectJs("../js/thermostat.js");
phantom.injectJs("jquery.min.js");
phantom.injectJs("sinon-1.17.3.js");
phantom.injectJs("sinon-server-1.17.3.js");

function setUp(context) {
	context.requests = this.requests = [];
	context.xhr = sinon.useFakeXMLHttpRequest();
   	context.xhr.onCreate = function (xhr) {
   		requests.push(xhr);
   	};
}

function tearDown(context) {
	context.xhr.restore();
}

casper.test.begin('get model', 2, function(test) {
	"use strict";
   	
	casper.start().then(function() {
		setUp(this);
		var callback = function(name) {
			test.assertEquals(name, "CT80", "Model name is correct");
		};
		getModel(callback);
		
		// Check we're in a reasonable starting state
		test.assertEquals(1, requests.length, "One request in sinan queue");
		
		this.requests[0].respond(200, { "Content-Type": "text/plain" }, 
			'{"model":"CT80 V2.14T"}');
		
		tearDown(this);
	}).run(function() {
		test.done();
	});
});

