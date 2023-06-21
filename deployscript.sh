#!/usr/bin/env bash

# print the variables, local_directory, remote_directory, ssh_server which are exported in the os
echo "local_directory: $local_directory"
echo "remote_directory: $remote_directory"
echo "ssh_server: $ssh_server"

ssh $ssh_server "if [ ! -d $remote_directory ]; then sudo mkdir $remote_directory; sudo chown \$(whoami):\$(whoami) $remote_directory; fi"

# Sync the local and remote directories using rsync, excluding files as per .gitignore
rsync -avz --exclude-from='.gitignore' --exclude='.git' $local_directory/ $ssh_server:$remote_directory

ssh $ssh_server "if ! dpkg -l | grep -q '^ii  python3.8-venv'; then sudo apt-get update; sudo apt-get install -y python3.8-venv; fi"

# Check if the venv directory exists in the remote directory
ssh $ssh_server "if [ ! -d $remote_directory/venv ]; then python3 -m venv $remote_directory/venv; fi"

# Check that venv was created properly
ssh $ssh_server "if [ -d $remote_directory/venv ]; then source $remote_directory/venv/bin/activate && pip install -r $remote_directory/requirements.txt; fi"

# Check that pip install ran properly
if [ $? -ne 0 ]
then
    echo "Error: Failed to install Python dependencies"
    exit 1
fi

echo "Deployment completed successfully"



