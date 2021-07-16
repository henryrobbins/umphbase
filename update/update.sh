#!/usr/bin/env bash

# Input Variables
HOST=$1
USERNAME=$2
PASSWORD=$3
# PATH=$4

# Pull newest data from ATU
python pull.py

# Upload this data to RDS
python sql_push.py arguments ${HOST} umphbase ${USERNAME} ${PASSWORD}