#! /bin/bash

[ -n "$(which virtualenv)" ] || 
	( echo "No virtualenv on the system.  Please install" ; exit 1 )

WD=$(pwd)

# make sure we're in the right directory
cd "$(dirname $0)"
virtualenv .
. bin/activate
#pip install -r CORSProxy/requirements.txt -r CORSProxy/dev-requirements.txt -r dev-requirements.txt
pip install -r dev-requirements.txt
#nodeenv -p -v
cd "$WD"
