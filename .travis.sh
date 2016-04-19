#!/bin/bash

EXIT_CODE=0
trap catch_errors ERR;
function catch_errors() {
  EXIT_CODE=$?
  echo "Exited with $EXIT_CODE"
}

cd remote_thermo_measurement
tox

if [ -n "${CODACY_PROJECT_TOKEN}" ]
then
	echo "Uploading coverage results to codacy..."
	pip install codacy-coverage
	pwd
	ls
	coverage xml
        python-codacy-coverage -r coverage.xml
fi
cd ..

exit $EXIT_CODE
