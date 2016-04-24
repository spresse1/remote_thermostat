// Constants
const thermoHostname="http://thermostat";
//Paths
const thermoInfo = "/tstat";
const thermoModel = "/tstat/model";
const thermoProgramHeat = "/tstat/program/heat";
const thermoProgramCool = "/tstat/program/cool";
// Human readable translations
const tmodes = ["Off", "Heat", "Cool", "Auto"];
const days = ["Monday", "Tuesday", "Wednesday", "Thursday",
	"Friday", "Saturday", "Sunday" ];
// Runtime state
var model = "Unknown";

function ajaxFailed(xhr, status, errorThrown) {
	alert( "Sorry, there was a problem! Server replied: " + 
		xhr.status + ": " + xhr.statusText );
	console.log( "Error: " + errorThrown );
	console.log( "Status: " + status );
}

function ajaxAlways(xhr, status) {
	//console.dir( xhr );
}

function getModel(callback) {
	$.ajax({
		url: thermoHostname + thermoModel,
		type: "GET",
		dataType: "json",
	})
	.done(function (json) {
		this.model = json.model.split(" ")[0];
		callback(this.model);
	})
	.fail(function (xhr, status, errorThrown) { 
		ajaxFailed(xhr, status, errorThrown)
	})
	.always(function (xhr, status) { ajaxAlways(xhr, status) })	
}

/*function loadProgram() {
	$.ajax({
		url: thermoHostname + thermoProgramHeat,
		type: "GET",
		dataType: "json",
	})
	.done(function (json) {
		programDiv = $( "#programDisplay" );
		for (day in json) {
programDiv.html = programDiv.html + 
	"<div id=\"programHeat" + days[day] + "\"></div>";
for (time in day) {

}
		}
	})
	.fail(function (xhr, status, errorThrown) { ajaxFailed(xhr, status, errorThrown) })
	.always(function (xhr, status) { ajaxAlways(xhr, status) })
	
}

function refresh() {

//$( "#fanStatus" ).text("Unavailable on this model");
	// Get current status
	$.ajax({
		url: thermoHostname + thermoInfo,
		type: "GET",
		dataType: "json",
	})
	// On success...
	.done(function( json ) {
		$( "#tempDisplay" ).text( json.temp )
		$( "#tstatState" ).text( tmodes[json.tstate] );
		$( "#tstatMode" ).text( tmodes[json.tmode] );
		
		if (json.fmode==1 || json.fmode==0 ) {
$( "#fanMode" ).text("auto");
		} else {
$( "#fanMode" ).text("on");
		}
	})
	.fail(function (xhr, status, errorThrown) { ajaxFailed(xhr, status, errorThrown) })
	.always(function (xhr, status) { ajaxAlways(xhr, status) })
	
}

$( document ).ready(function () {
	$("#showProgramLink").click(function (e) { e.preventDefault;
		alert("Loading programs");
		loadProgram();
	});

	// Do stuff that happens at init 
	refresh();
})*/
