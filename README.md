# remote_thermostat
Code and files related to my Radio Thermostat Company of America CT-50.  
The thermostat used here can be purchased at 
[Amazon](http://www.amazon.com/dp/B00KQS35XA/).  This thermostat is 
extremely geek-friendly, having an 
[open 
API](http://assistly-production.s3.amazonaws.com/91626/kb_article_attachments/38350/RTCOAWiFIAPIV1_3_original.pdf?AWSAccessKeyId=AKIAJNSFWOZ6ZS23BMKQ&Expires=1459096179&Signature=A7XvkHItaEVmWlsl2BrbRasrKIk%3D&response-content-disposition=filename%3D%22RTCOAWiFIAPIV1_3.pdf%22&response-content-type=application%2Fpdf).  
It is also security-nut friendly, as it doesn't require a cloud 
connection to use.  Unfortunately, this does mean some functionality is 
unavailable.  These projects are intended to bridge the gaps to make it 
equally functional for non-cloud installations.  It is my hope that 
these will eventually surpass the default cloud in terms of usefulness 
and functionality.

I am looking for firmware images (RTCOA refuses to give them out unless 
there's a security update) or documentation on the cloud API.  If you 
have either of these, please contact me!

This project is deliberately GPL so that RTCOA must acknowledge it if it 
should become something they wish to use.

# Subprojects
This repository has several subprojects, which have different purposes.  
These can be used together or individually.

## remote_thermo_measurement
This is a simple proof-of-concept daemon to read the temperature from a 
location other than where the thermostat is.  It assumes it is running 
on a system identical to [this 
tutorial](https://learn.adafruit.com/measuring-temperature-with-a-beaglebone-black/overview).  
If you do not have this hardware, it should serve as a reasonable 
example of how to implement the networked portion of this functionality.  
In the future, it may be expanded to include more hardware.  If you 
write a similar tool (no matter how ugly). let me know and we'll work to 
integrate it.

## web_interface

This is a (relatively) simple interface you can use to control the 
thermostat's settings.  Design recommendations welcome!

requires api_proxy.

## api_proxy

This project has two purposes:
1. To proxy API requests.  web_interface cannot make requests directly 
against the thermostat due to CSRF protections and CORS.  The thermostat 
doesn't set the appropriate headers to enable remote requests.  This API 
either acts to proxy requests for a web_interface instance on the same 
host or adds the additional headers necessary for hosts somehere else to 
make requests.
2. To add authentication.  This makes it suitable to expose to a wider 
network than merely your home, possibly allowing exposure to the 
internet.  Note that I still recommend not doing so and instead using 
SSH tunnels or a VPN to access the thermostat/web interface remotely.
