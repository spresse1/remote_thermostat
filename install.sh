#! /bin/bash

[ -z "$( which unzip )" ] && ( echo "Please install the unzip utility"; exit 1 )
cd /tmp
wget https://github.com/mhrivnak/radiotherm/archive/master.zip
unzip -f master.zip
rm master.zip
cd radiotherm-master
python setup.py install
cd ..
rm -r radiotherm-master
pip install -U Adafruit_BBIO requests
