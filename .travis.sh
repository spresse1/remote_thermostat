#!/bin/bash

cd remote_thermo_measurement
tox
if [ -n "${CODACY_PROJECT_TOKEN}"]
then
	pip install codacy-coverage
	coverage xml
        python-codacy-coverage -r coverage.xml
fi
cd ..
