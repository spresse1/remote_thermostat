/**
 * Tests for ThermoComms.
 */

QUnit.module("Thermostat Communication (ThermoComms)", function(hooks) {
	hooks.beforeEach( function() {
		console.log("Running beforeEach");
		this.server = sinon.fakeServer.create();
	});
	
	hooks.afterEach( function() {
		console.log("running afterEach");
		this.server.restore();
	});

	QUnit.test('get model',function(test) {
		var done = test.async();
		this.tcomms = new ThermoComms("localhost");

		var callback = function(name, version) {
			console.log("Given result of", name, version)
			test.ok(name==="CT80", "Model name is correct");
			test.ok(version==="V2.14T", "Version ID is correct");
			done();
		};
	
		this.tcomms.getModelVersion(callback);
		this.server.requests[0].respond(200, { "Content-Type": "text/plain" }, 
			'{"model":"CT80 V2.14T"}');
	});

	QUnit.test('Test AJAX failure code',function(test) {
		var done = test.async();
		this.tcomms = new ThermoComms("localhost")
		
		var cb_failure = function(xhr, status, errorThrown) {
			console.log("In failure branch.");
			ThermoComms.ajaxFailed(xhr, status, errorThrown);
			test.ok(true, "Called into failure code");
			done();
		}
	
		var cb_success = function(name) {
			console.log("In success mode");
			test.ok(false, "Called into failure code");
			done();
		}
	
		console.log("About to call into function under test");
		this.tcomms.getModelVersion(cb_success, cb_failure);
		this.server.requests[0].respond(404, {}, "");

	});

	QUnit.test('default address in constructor',function(test) {
		this.tcomms = new ThermoComms();
		
		test.ok(this.tcomms.address=="localhost");
	});

	QUnit.test('Specify protocol',function(test) {
		this.tcomms = new ThermoComms("localhost","foobar");
		
		test.ok(this.tcomms.protocol=="foobar");
	});
});
