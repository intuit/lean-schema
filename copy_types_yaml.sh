#! /usr/bin/env bash

if [[ $1 ]]
then
    if [[ -e $1 ]]
    then
        echo "Types YAML file $1 exists, copying it"
        cp $1 $2
    else
        echo "Types YAML file $1 does not exist, ignoring it"
        exit 0
    fi
else
    echo "Types YAML property is not set, not copying anything"
fi
