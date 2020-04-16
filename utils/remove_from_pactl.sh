#!/bin/bash

# This script will list all pulse audio devices connected

# If you notice your mic has zero input channels then it's a good idea to unload it using pactl


pactl list > pactl_list.txt

echo 'find the mic you want to unload in pactl_list.txt'

echo 'unload it using "pactl unload-module X" where X is the number of the module'


