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
	if (address!==undefined){
		this.address = address;
	} else {
		this.address = "localhost";
	}
	
	this.protocol = ( protocol !== undefined ) ? protocol : "http"
	this.thermoInfo = "/tstat";
	this.thermoModel = "/tstat/model";
	this.thermoProgramHeat = "/tstat/program/heat";
	this.thermoProgramCool = "/tstat/program/cool";
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
	$.ajax({
		url: this.protocol + "://" + this.address + this.thermoModel,
		type: "GET",
		dataType: "json",
	})
	.done(function (json) {
		model = json.model.split(" ")[0];
		version = json.model.split(" ")[1];
		console.log("Recieved result of", model, version);
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
	})
}


