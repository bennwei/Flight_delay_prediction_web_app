#!/usr/bin/env bash

#
# Script to install jq utility locally, across all platforms (hopefully)
#
export PROJECT_HOME=`pwd`

echo "This script will install the utility jq locally in '$PROJECT_HOME/bin' ..."

echo "Making bin directory"
mkdir bin

echo "Adding '$PROJECT_HOME/bin' to \$PATH ..."
export PATH=$PATH:$PROJECT_HOME/bin

echo "Creating backup of '~/.bash_profile' to '~/.bash_profile.jq_install.bak' ..."
cp ~/.bash_profile ~/.bash_profile.jq_install.bak

echo "Adding \$PROJECT_HOME/bin to ~/.bash_profile"
echo "" >> ~/.bash_profile
echo "# Added by $PROJECT_HOME/jq_install.sh" >> ~/.bash_profile
echo "export PATH=$PATH:$PROJECT_HOME/bin" >> ~/.bash_profile
echo "" >> ~/.bash_profile

echo "Detecting platform ..."
if [ "$(uname)" == "Darwin" ]; then
  PLATFORM="Darwin"
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
  PLATFORM="Linux"
elif [ "$(expr substr $(uname -s) 1 10)" == "MINGW32_NT" ]; then
  PLATFORM="Windows"
fi
echo "Platform is '$PLATFORM' ..."

echo "Performing installation for platform '$PLATFORM' ..."
if [ $PLATFORM == "Darwin" ]; then
  echo "Detecting Mac frameworks (must have Homebrew or MacPorts installed) ..."
  if [ ! -z `which brew` ]; then
    echo "Homebrew detected, performing install via homebrew ..."
    brew install jq
  elif [ ! -z `which port` ]; then
    echo "MacPorts detected, performing install via MacPorts ..."
    echo "Executing sudo: 'sudo port install jq'"
    sudo port install jq
  else
    # If neither homebrew or macports are detected, exit
    echo "Install failed."
    echo "Please install Homebrew or MacPorts to continue installation. Or see install directions (including from source) at https://github.com/stedolan/jq/wiki/Installation#or-build-from-source"
    echo ""
    exit 1
  fi
elif [ $PLATFORM == "Linux" ]; then
  echo "Detecting Debian/Ubuntu ..."
  if [ ! -z `python -mplatform | grep debian` ]; then
    echo "Debian/Ubuntu detected. Performing 'apt-get install jq' ..."
    sudo apt-get install -y jq
  else
    echo "CentOS detected. Detecting 'dnf' ..."
    if [ -z `which dnf` ]; then
      echo "Detected dnf! Performing sudo!: 'sudo dnf install jq' ..."
      sudo dnf install jq
    else
      echo "dnf not detected! Using yum. Performing sudo!: 'sudo yum install jq' ..."
      sudo yum install jq
    fi
  fi
elif [$PLATFORM == "Windows" ]; then
  echo "Using choco to install jq ..."
  choco install jq
fi

echo ""
echo "Installation complete. If you have any issues, try the install instructions for jq at https://github.com/stedolan/jq/wiki/Installation"
echo ""