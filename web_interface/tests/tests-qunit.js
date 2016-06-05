QUnit.module("Thermostat model info (getModel()) functions", function(hooks) {
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
		var callback = function(name) {
			test.ok(name==="CT80", "Model name is correct");
			done();
		};
	
		getModel(callback);
		this.server.requests[0].respond(200, { "Content-Type": "text/plain" }, 
			'{"model":"CT80 V2.14T"}');
	});

	QUnit.test('Test AJAX failure code',function(test) {
		var done = test.async();
		
		var cb_failure = function(xhr, status, errorThrown) {
			console.log("In failure branch.");
			ajaxFailed(xhr, status, errorThrown);
			test.ok(true, "Called into failure code");
			done();
		}
	
		var cb_success = function(name) {
			console.log("In success mode");
			test.ok(false, "Called into failure code");
			done();
		}
	
		console.log("About to call into function under test");
		getModel(cb_success, cb_failure);
		this.server.requests[0].respond(404, {}, "");

	});
});
