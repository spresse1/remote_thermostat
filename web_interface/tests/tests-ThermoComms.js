/**
 * Tests for ThermoComms.
 */
/*global
QUnit, ThermoComms, sinon
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
	
	QUnit.module("ThermoComms.constructor", function() {
		QUnit.test("default address in constructor",function(test) {
			this.tcomms = new ThermoComms();
		
			test.ok(this.tcomms.address==="localhost");
		});

		QUnit.test("Specify protocol",function(test) {
			this.tcomms = new ThermoComms("localhost","foobar");
		
			test.ok(this.tcomms.protocol==="foobar");
		});
	});

	QUnit.module("ThermoComs.getModelVersion", function() {
		QUnit.test('get model',function(test) {
			var done = test.async();
			this.tcomms = new ThermoComms("localhost");
			var testOb = this;

			var callback = function(name, version) {
				console.log("Given result of", name, version);
				test.ok(name==="CT80", "Model name is correct");
				test.ok(version==="V2.14T", "Version ID is correct");
				test.ok(testOb.tcomms.model==="CT80", "Object has model set");
				test.ok(
					testOb.tcomms.version==="V2.14T",
					"Object has version set");
				done();
			};
	
			this.tcomms.getModelVersion(callback);
			this.server.requests[0].respond(200, { "Content-Type": "text/plain" }, 
				'{"model":"CT80 V2.14T"}');
		});

		QUnit.test("Test AJAX failure code",function(test) {
			var done = test.async();
			this.tcomms = new ThermoComms("localhost");
		
			var cb_failure = function(xhr, status, errorThrown) {
				console.log("In failure branch.");
				ThermoComms.ajaxFailed(xhr, status, errorThrown);
				test.ok(true, "Called into failure code");
				done();
			};
	
			var cb_success = function(name) {
				console.log("In success mode");
				test.ok(false, "Called into failure code");
				done();
			};
	
			console.log("About to call into function under test");
			this.tcomms.getModelVersion(cb_success, cb_failure);
			this.server.requests[0].respond(404, {}, "");

		});
	});
	
	QUnit.module("ThermoComms.getState", function(hooks) {
		hooks.beforeEach( function() {
			console.log("Running beforeEach in getState");
			this.server = sinon.fakeServer.create();
			this.tcomms = new ThermoComms("localhost");
			this.tcomms.model="CT80";
			this.tcomms.version="3.15";
		});
		
		QUnit.test("Basic GetState, model unset", function(test) {
			var done = test.async();
			var cb_success = function(json) {
				console.log("In success mode");
				test.ok(true, "Call is success");
				test.equal(json.temp, 45.6, "Temperature set correctly");
				test.equal(json.hvac_state, 0, "hvac_state set correctly");
				test.equal(json.fan_state, 0, "fan_state set correctly");
				test.deepEqual(json.time, {"day": 0, "hour": 1, "minutes": 2 },
					"time set correctly");
				done();
			};
			
			this.tcomms.model=undefined;
			this.tcomms.version=undefined;

			this.tcomms.getState(cb_success);
			this.server.requests[0].respond(200, { "Content-Type": "text/plain" }, 
				'{"model":"CT80 V2.14T"}');
			this.server.requests[1].respond(200, { "Content-Type": "text/plain" }, 
				'{' +
					'"temp": 45.6, ' +
					'"ttarget": 0, ' +
					'"fmode": 0, ' +
					'"time": {"day": 0, "hour": 1, "minutes": 2} ' +
				'}');
		});
		
		QUnit.test("getState fan on", function(test) {
			var done = test.async();
			var cb_success = function(json) {
				console.log("In success mode");
				test.ok(true, "Call is success");
				test.equal(json.temp, 45.6, "Temperature set correctly");
				test.equal(json.hvac_state, 0, "hvac_state set correctly");
				test.equal(json.fan_state, 1, "fan_state set correctly");
				test.deepEqual(json.time, {"day": 0, "hour": 1, "minutes": 2 },
					"time set correctly");
				done();
			};

			this.tcomms.getState(cb_success);
			this.server.requests[0].respond(
				200, { "Content-Type": "text/plain" }, 
				'{"temp": 45.6, "ttarget": 0, "fmode": 2, ' +
				'"time": {"day": 0, "hour": 1, "minutes": 2} }');
		});
		
		QUnit.test("getState CT30", function(test) {
			var done = test.async();
			var cb_success = function(json) {
				console.log("In success mode");
				test.ok(true, "Call is success");
				test.equal(json.temp, 45.6, "Temperature set correctly");
				test.equal(json.hvac_state, 0, "hvac_state set correctly");
				test.equal(json.fan_state, 0, "fan_state set correctly");
				test.deepEqual(json.time, {"day": 0, "hour": 1, "minutes": 2 },
					"time set correctly");
				done();
			};

			this.tcomms.model = "CT30";
			this.tcomms.getState(cb_success);
			this.server.requests[0].respond(
				200, { "Content-Type": "text/plain" }, 
				'{"temp": 45.6, "ttarget": 0, "fstate": 0, ' +
				'"time": {"day": 0, "hour": 1, "minutes": 2} }');
		});
		
		QUnit.test('Test AJAX failure code',function(test) {
			var done = test.async();
		
			var cb_failure = function(xhr, status, errorThrown) {
				console.log("In failure branch.");
				ThermoComms.ajaxFailed(xhr, status, errorThrown);
				test.ok(true, "Called into failure code");
				done();
			};
	
			var cb_success = function(name) {
				console.log("In success mode");
				test.ok(false, "Called into failure code");
				done();
			};
	
			console.log("About to call into function under test");
			this.tcomms.getState(cb_success, cb_failure);
			this.server.requests[0].respond(404, {}, "");

		});
	});
	
	QUnit.module("ThermoComms.getTarget", function(hooks) {
		hooks.beforeEach( function() {
			console.log("Running beforeEach in getTarget");
			this.server = sinon.fakeServer.create();
			this.tcomms = new ThermoComms("localhost");
			this.tcomms.model="CT80";
			this.tcomms.version="3.15";
		});
		
		QUnit.test("Basic getTarget", function(test) {
			var done = test.async();
			var cb_success = function(json) {
				console.log("In success mode");
				test.ok(true, "Call is success");
				test.equal(json.temp, 43.5, "Temperature set correctly");
				test.equal(json.hvac_mode, 0, "hvac_state set correctly");
				test.equal(json.fan_mode, 0, "fan_state set correctly");
				test.equal(json.program.mode, 0, "program set correctly");
				test.equal(json.program.override, 0, 
					"program override set correctly");
				test.equal(json.program.hold, 0, "Program hold set correctly");
				done();
			};
			
			this.tcomms.model=undefined;
			this.tcomms.version=undefined;

			this.tcomms.getTarget(cb_success);
			this.server.requests[0].respond(200, { "Content-Type": "text/plain" }, 
				'{"model":"CT80 V2.14T"}');
			this.server.requests[1].respond(200, { "Content-Type": "text/plain" }, 
				'{' +
					'"t_heat": 43.5, ' +
					'"tmode": 0, ' +
					'"fmode": 0, ' +
					'"program_mode": 0, ' +
					'"override": 0, ' +
					'"hold": 0 ' +
				'}');
		});
		
		QUnit.test("getTarget fan on", function(test) {
			var done = test.async();
			var cb_success = function(json) {
				console.log("In success mode");
				test.ok(true, "Call is success");
				test.equal(json.temp, 43.5, "Temperature set correctly");
				test.equal(json.hvac_mode, 0, "hvac_state set correctly");
				test.equal(json.fan_mode, 1, "fan_state set correctly");
				test.equal(json.program.mode, 0, "program set correctly");
				test.equal(json.program.override, 0, 
					"program override set correctly");
				test.equal(json.program.hold, 0, "Program hold set correctly");
				done();
			};
			
			this.tcomms.model=undefined;
			this.tcomms.version=undefined;

			this.tcomms.getTarget(cb_success);
			this.server.requests[0].respond(200, { "Content-Type": "text/plain" }, 
				'{"model":"CT80 V2.14T"}');
			this.server.requests[1].respond(200, { "Content-Type": "text/plain" }, 
				'{"t_heat": 43.5, "tmode": 0, "fmode": 2, "program_mode": 0, ' +
					'"override": 0, "hold": 0 }');
		});
		
		QUnit.test("getTarget t_cool", function(test) {
			var done = test.async();
			var cb_success = function(json) {
				console.log("In success mode");
				test.ok(true, "Call is success");
				test.equal(json.temp, 43.5, "Temperature set correctly");
				test.equal(json.hvac_mode, 0, "hvac_state set correctly");
				test.equal(json.fan_mode, 1, "fan_state set correctly");
				test.equal(json.program.mode, 0, "program set correctly");
				test.equal(json.program.override, 0, 
					"program override set correctly");
				test.equal(json.program.hold, 0, "Program hold set correctly");
				done();
			};
			
			this.tcomms.model=undefined;
			this.tcomms.version=undefined;

			this.tcomms.getTarget(cb_success);
			this.server.requests[0].respond(200, { "Content-Type": "text/plain" }, 
				'{"model":"CT80 V2.14T"}');
			this.server.requests[1].respond(200, { "Content-Type": "text/plain" }, 
				'{"t_cool": 43.5, "tmode": 0, "fmode": 2, "program_mode": 0, ' +
					'"override": 0, "hold": 0 }');
		});
		
		QUnit.test("getTarget it_heat", function(test) {
			var done = test.async();
			var cb_success = function(json) {
				console.log("In success mode");
				test.ok(true, "Call is success");
				test.equal(json.temp, 43.5, "Temperature set correctly");
				test.equal(json.hvac_mode, 0, "hvac_state set correctly");
				test.equal(json.fan_mode, 1, "fan_state set correctly");
				test.equal(json.program.mode, 0, "program set correctly");
				test.equal(json.program.override, 0, 
					"program override set correctly");
				test.equal(json.program.hold, 0, "Program hold set correctly");
				done();
			};
			
			this.tcomms.model=undefined;
			this.tcomms.version=undefined;

			this.tcomms.getTarget(cb_success);
			this.server.requests[0].respond(200, { "Content-Type": "text/plain" }, 
				'{"model":"CT80 V2.14T"}');
			this.server.requests[1].respond(200, { "Content-Type": "text/plain" }, 
				'{"it_heat": 43.5, "tmode": 0, "fmode": 2, "program_mode": 0, ' +
					'"override": 0, "hold": 0 }');
		});
		
		QUnit.test("getTarget it_cool", function(test) {
			var done = test.async();
			var cb_success = function(json) {
				console.log("In success mode");
				test.ok(true, "Call is success");
				test.equal(json.temp, 43.5, "Temperature set correctly");
				test.equal(json.hvac_mode, 0, "hvac_state set correctly");
				test.equal(json.fan_mode, 1, "fan_state set correctly");
				test.equal(json.program.mode, 0, "program set correctly");
				test.equal(json.program.override, 0, 
					"program override set correctly");
				test.equal(json.program.hold, 0, "Program hold set correctly");
				done();
			};
			
			this.tcomms.model=undefined;
			this.tcomms.version=undefined;

			this.tcomms.getTarget(cb_success);
			this.server.requests[0].respond(200, { "Content-Type": "text/plain" }, 
				'{"model":"CT80 V2.14T"}');
			this.server.requests[1].respond(200, { "Content-Type": "text/plain" }, 
				'{"it_cool": 43.5, "tmode": 0, "fmode": 2, "program_mode": 0, ' +
					'"override": 0, "hold": 0 }');
		});
		
		QUnit.test("getTarget a_heat", function(test) {
			var done = test.async();
			var cb_success = function(json) {
				console.log("In success mode");
				test.ok(true, "Call is success");
				test.equal(json.temp, 43.5, "Temperature set correctly");
				test.equal(json.hvac_mode, 0, "hvac_state set correctly");
				test.equal(json.fan_mode, 1, "fan_state set correctly");
				test.equal(json.program.mode, 0, "program set correctly");
				test.equal(json.program.override, 0, 
					"program override set correctly");
				test.equal(json.program.hold, 0, "Program hold set correctly");
				done();
			};
			
			this.tcomms.model=undefined;
			this.tcomms.version=undefined;

			this.tcomms.getTarget(cb_success);
			this.server.requests[0].respond(200, { "Content-Type": "text/plain" }, 
				'{"model":"CT80 V2.14T"}');
			this.server.requests[1].respond(200, { "Content-Type": "text/plain" }, 
				'{"a_heat": 43.5, "tmode": 0, "fmode": 2, "program_mode": 0, ' +
					'"override": 0, "hold": 0 }');
		});
		
		QUnit.test("getTarget a_cool", function(test) {
			var done = test.async();
			var cb_success = function(json) {
				console.log("In success mode");
				test.ok(true, "Call is success");
				test.equal(json.temp, 43.5, "Temperature set correctly");
				test.equal(json.hvac_mode, 0, "hvac_state set correctly");
				test.equal(json.fan_mode, 1, "fan_state set correctly");
				test.equal(json.program.mode, 0, "program set correctly");
				test.equal(json.program.override, 0, 
					"program override set correctly");
				test.equal(json.program.hold, 0, "Program hold set correctly");
				done();
			};
			
			this.tcomms.model=undefined;
			this.tcomms.version=undefined;

			this.tcomms.getTarget(cb_success);
			this.server.requests[0].respond(200, { "Content-Type": "text/plain" }, 
				'{"model":"CT80 V2.14T"}');
			this.server.requests[1].respond(200, { "Content-Type": "text/plain" }, 
				'{"a_cool": 43.5, "tmode": 0, "fmode": 2, "program_mode": 0, ' +
					'"override": 0, "hold": 0 }');
		});
		
		QUnit.test("getTarget no temp", function(test) {
			var done = test.async();
			var cb_success = function(json) {
				console.log("In success mode");
				test.ok(true, "Call is success");
				test.equal(json.temp, -1, "Temperature set correctly");
				test.equal(json.hvac_mode, 0, "hvac_state set correctly");
				test.equal(json.fan_mode, 0, "fan_state set correctly");
				test.equal(json.program.mode, 0, "program set correctly");
				test.equal(json.program.override, 0, 
					"program override set correctly");
				test.equal(json.program.hold, 0, "Program hold set correctly");
				done();
			};
			
			this.tcomms.model=undefined;
			this.tcomms.version=undefined;

			this.tcomms.getTarget(cb_success);
			this.server.requests[0].respond(200, { "Content-Type": "text/plain" }, 
				'{"model":"CT80 V2.14T"}');
			this.server.requests[1].respond(200, { "Content-Type": "text/plain" }, 
				'{"tmode": 0, "fmode": 0, "program_mode": 0, ' +
					'"override": 0, "hold": 0 }');
		});
		
		QUnit.test('Test AJAX failure code',function(test) {
			var done = test.async();
		
			var cb_failure = function(xhr, status, errorThrown) {
				console.log("In failure branch.");
				ThermoComms.ajaxFailed(xhr, status, errorThrown);
				test.ok(true, "Called into failure code");
				done();
			};
	
			var cb_success = function(name) {
				console.log("In success mode");
				test.ok(false, "Called into failure code");
				done();
			};
	
			console.log("About to call into function under test");
			this.tcomms.getTarget(cb_success, cb_failure);
			this.server.requests[0].respond(404, {}, "");

		});
	});
});
