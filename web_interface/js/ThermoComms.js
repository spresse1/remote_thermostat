/**
 * A library-internal class to manage communication with the thermostat.  More
 * or less an AJAx wrapper that is very specific to this API.
 * Parameters:
 *   address - the network address of the thermostat.  Defaults to localhost.
 *     though this is unlikely to be what you want if you're not running a 
 *     proxy.
 *   protocol - The string representing the protocol to use connecting to the
 *     thermostat.  If not explicitly set, defaults to "http"
 */
var ThermoComms = function(address, protocol) {
	if (typeof address !== "undefined"){
		this.address = address;
	} else {
		this.address = "localhost";
	}
	
	this.protocol = ( typeof protocol !== "undefined" ) ? protocol : "http";
	this.thermoInfo = "/tstat";
	this.thermoModel = "/tstat/model";
	this.thermoProgramHeat = "/tstat/program/heat";
	this.thermoProgramCool = "/tstat/program/cool";
	
	// Alas, we need to keep track of the model.
	this.model = undefined;
	this.version = undefined;
};

ThermoComms.ajaxFailed = function(xhr, status, errorThrown) {
	alert( "Sorry, there was a problem! Server replied: " + 
		xhr.status + ": " + xhr.statusText );
	console.log( "Error: " + errorThrown );
	console.log( "Status: " + status );
}

ThermoComms.ajaxAlways = function(xhr, status) {
	console.log("Request returned ", status, " full listing follows");
	console.dir( xhr );
}

/**
 * Fetches/updates the model and version of a thermostat.
 * Returns nothing.
 * Callback prototypes:
 *   success_cb(model, version):
 *     model - the model name returned by the thermostat.  Example: CT80
 *     version - the version number (including V, if applicable) returned by
 *       the thermostat.  Example: V1.94
 *   fail_cb(xhr, status, errorThrown)
 *     See jQuery's ajax.fail() for details.
 */
ThermoComms.prototype.getModelVersion = function(success_cb, fail_cb) {
	if (this.model && this.version) {
		success_cb(this.model, this.verison)
	}
	
	var tcommObject = this
	
	$.ajax({
		url: this.protocol + "://" + this.address + this.thermoModel,
		type: "GET",
		dataType: "json",
	})
	.done(function (json) {
		var model = json.model.split(" ")[0];
		var version = json.model.split(" ")[1];
		console.log("Recieved result of", model, version);
		
		tcommObject.model = model;
		tcommObject.version = version;
		
		success_cb(model, version);
	})
	.fail(function (xhr, status, errorThrown) {
		/* istanbul ignore else */
		if (fail_cb !== undefined) {
			fail_cb(xhr, status, errorThrown)
		} else {
			ThermoComms.ajaxFailed(xhr, status, errorThrown)
		}
	})
	.always(function (xhr, status) {
		ThermoComms.ajaxAlways(xhr, status)
	});
}

/**
 * Fetches/updates the (volatile) state of the thermostat
 * Returns nothing
 * Callback prototypes:
 *   success_cb(structure):
 *     A structure, built as follows:
 *       {
 *         temp: float, // The current temp
 *         hvac_state: int, // 0=off, 1= heat, 2=cool
 *         fan_state: int, // Fan mode 0=off, 1=on
 *         time:
 *           day: int, // Day of the week
 *           hour: int, // Hour of the day
 *           minute: int, // minute of the hour
 *       }
 *   fail_cb(xhr, status, errorThrown)
 *     See jQuery's ajax.fail() for details.
 */
ThermoComms.prototype.getState = function(success_cb, fail_cb) {
	var context = this;
	// We need to know what model, wrap the whole call as the CB to getting that
	this.getModelVersion(function() {
		$.ajax({
			url: context.protocol + "://" + context.address + context.thermoInfo,
			type: "GET",
			dataType: "json",
		})
		.done(function (json) {
			console.log("Recieved result of", json);
		
			var result = {}
		
			result.temp = json.temp
			result.hvac_state = json.ttarget
			if (context.model === "CT30") {
				result.fan_state = json.fstate;
			} else {
				result.fan_state = ( json.fmode >=1 ) ? 1 : 0
			}
			result.time = json.time
		
			success_cb(result);
		})
		.fail(function (xhr, status, errorThrown) {
			/* istanbul ignore else */
			if (fail_cb !== undefined) {
				fail_cb(xhr, status, errorThrown)
			} else {
				ThermoComms.ajaxFailed(xhr, status, errorThrown)
			}
		})
		.always(function (xhr, status) {
			ThermoComms.ajaxAlways(xhr, status)
		})
	}, fail_cb);
}

/**
 * Fetches/updates the (volatile) state of the thermostat
 * Returns nothing
 * Callback prototypes:
 *   success_cb(structure):
 *     A structure, built as follows:
 *       {
 *         temp: float, // The target termperature fo rhte thermostat
 *         hvac_mode: str, // One of {off, auto, heat, cool}. Operating mode
 *         fan_mode: str, // 0 = Auto, 1= (always) on
 *         program: {
 *           mode: int, // 0= A, 1= B, 2=vacation, 3=Holiday
 *           override: int, // Whether or not he target is an
 *                           // override of the program 0= no, 1 = yes
 *           hold: bool, // Whether the thermostat will hold this temperature
 *                       // 0 = off, 1 = on
 *       }
 *   fail_cb(xhr, status, errorThrown)
 *     See jQuery's ajax.fail() for details.
 */
ThermoComms.prototype.getTarget = function(success_cb, fail_cb) {
	var context = this;
	// We need to know what model, wrap the whole call as the CB to getting that
	this.getModelVersion(function() {
	 	$.ajax({
			url: context.protocol + "://" + context.address + context.thermoInfo,
			type: "GET",
			dataType: "json",
		})
		.done(function (json) {
			console.log("Recieved result of", json);
		
			var result = {}
		
			// Figure out what temperature to read
			if (json.t_heat) {
				result.temp = json.t_heat;
			} else if (json.t_cool) {
				result.temp = json.t_cool;
			} else if (json.it_heat) {
				result.temp = json.it_heat;
			} else if (json.it_cool) {
				result.temp = json.it_cool;
			} else if (json.a_heat) {
				result.temp = json.a_heat;
			} else if (json.a_cool) {
				result.temp = json.a_cool;
			} else {
				result.temp = -1
			}
			result.hvac_mode = json.tmode;
			result.fan_mode = ( json.fmode <=1 ) ? 0 : 1 ;
		
			result.program = {}
			result.program.mode = json.program_mode
			result.program.override = json.override
			result.program.hold = json.hold
			
			success_cb(result);
		})
		.fail(function (xhr, status, errorThrown) {
			/* istanbul ignore else */
			if (fail_cb !== undefined) {
				fail_cb(xhr, status, errorThrown);
			} else {
				ThermoComms.ajaxFailed(xhr, status, errorThrown);
			}
		})
		.always(function (xhr, status) {
			ThermoComms.ajaxAlways(xhr, status);
		})
	}, fail_cb);
}
