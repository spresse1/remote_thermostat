#!/bin/bash

EXIT_CODE=0
trap catch_errors ERR;
function catch_errors() {
  EXIT_CODE=$?
  echo "Exited with $EXIT_CODE"
}

cd remote_thermo_measurement
tox

exit $EXIT_CODE
