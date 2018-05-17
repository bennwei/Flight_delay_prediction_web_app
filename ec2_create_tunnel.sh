#!/usr/bin/env bash

EC2_HOSTNAME=`cat ./.ec2_hostname`
if [ -z $EC2_HOSTNAME ]; then
  echo ""
  echo "No hostname detected in '.ec2_hostname' :( Exiting!"
  echo ""
  echo "The command to create an ssh tunnel to port 5000 of your ec2 instance is: ssh -R 5000:localhost:5000 ubuntu@<ec2_hostname>"
  echo ""
  exit
fi

echo ""
echo "This script will create an ssh tunnel between the ec2 host's port 5000 and your local port 5000."
echo "This will enable you to view web applications you run from ex. Agile_Data_Code_2/ch08/web to be viewed at http://localhost:5000"
echo "Note: the tunnel will run in the background, and will die when you terminate the EC2 instance."
echo ""

# Create a tunnel to our ssh instance, port 5000 and map it to localhost:5000
echo "First we will forward the port the web appliations use..."
echo "Forwarding the remote machine's port 5000 to the local port 5000, which you can then access at http://localhost:5000"
echo 'Executing: ssh -N -i ./agile_data_science.pem -o StrictHostKeyChecking=no -L 5000:localhost:5000 ubuntu@$EC2_HOSTNAME &'
ssh -N -i ./agile_data_science.pem -o StrictHostKeyChecking=no -L 5000:localhost:5000 ubuntu@$EC2_HOSTNAME &
echo ""

# Create a tunnel for port 8888 for Jupyter notebooks
echo "Next we will forward the port the Jupyter Notebooks use..."
echo "Forwarding the remote machine's port 8888 to the local port 8888, which you can then access at http://localhost:8888"
echo 'Executing: ssh -N -i ./agile_data_science.pem -o StrictHostKeyChecking=no -L 8888:localhost:8888 ubuntu@$EC2_HOSTNAME &'
ssh -N -i ./agile_data_science.pem -o StrictHostKeyChecking=no -L 8888:localhost:8888 ubuntu@$EC2_HOSTNAME &
echo ""

# Create a tunnel for port 8080 for Airflow
echo "Next we will forward the port that Airflow uses..."
echo "Forwarding the remote machine's port 8080 to the local port 8080, which you can then access at http://localhost:8080"
echo 'Executing: ssh -N -i ./agile_data_science.pem -o StrictHostKeyChecking=no -L 8080:localhost:8080 ubuntu@$EC2_HOSTNAME &'
ssh -N -i ./agile_data_science.pem -o StrictHostKeyChecking=no -L 8080:localhost:8080 ubuntu@$EC2_HOSTNAME &
echo ""
