#!/bin/bash

EXIT_CODE=0
trap catch_errors ERR;
function catch_errors() {
  EXIT_CODE=$?
  echo "Exited with $EXIT_CODE"
}

cd remote_thermo_measurement
tox
tox -e codacy-coverage-upload

exit $EXIT_CODE
