#!/usr/bin/env bash
# Installation script for python3 in order to support various package managers.
# This script specifically targets:
#   * apt-get (debian)
#   * brew    (mac os)

if [[ ! `which python3` ]]; then
    echo "Could not find 'python3'; starting automatic install..."

    if [[ `which brew` ]]; then
        echo "Found brew (mac os)"
        brew install python3
    elif [[ `which apt-get` ]]; then
        echo "Found apt-get (debian)"
        sudo apt-get install python3
    else
        echo "Could not find a supported package manager. Please install python3 manually and run this install script again."
        exit 1
    fi
fi

if [[ ! `which pip3` ]]; then
    echo "Could not find 'pip3'; starting automatic install..."

    if [[ `which brew` ]]; then
        echo "Found brew (mac os)"
        echo "pip3 should have been installed in a previous step. Please install pip3 manually and run this install script again."
        exit 1
    elif [[ `which apt-get` ]]; then
        echo "Found apt-get (debian)"
        sudo apt-get install python3-pip
    else
        echo "Could not find a supported package manager. Please install pip3 manually and run this install script again."
        exit 1
    fi
fi
