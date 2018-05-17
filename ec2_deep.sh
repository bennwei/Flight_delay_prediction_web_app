#!/usr/bin/env bash

echo ""
echo "Welcome to Agile Data Science 2.0 - Deep Learning"
echo ""
echo "I will launch an g2.8xlarge instance in the default VPC for you, using a key and security group we will create."
echo ""

# Get the default region to launch in
echo "Fetching default region for our EC2 instance ..."
DEFAULT_REGION=`aws configure get region`
UBUNTU_DEEP_LEARNING_IMAGE_ID='ami-7fd7c906' # See https://aws.amazon.com/marketplace/pp/B06VSPXKDX

echo "Detecting external IP address ..."
EXTERNAL_IP=`dig +short myip.opendns.com @resolver1.opendns.com`

# Launch our instance, store the ReservationId in a file
echo ""
echo "Initializing EBS optimized g2.8xlarge EC2 instance in region '$DEFAULT_REGION' with security group 'agile_data_science', key name 'agile_data_science' and image id '$UBUNTU_IMAGE_ID' using the script 'aws/ec2_bootstrap.sh'"
aws ec2 run-instances \
    --image-id $UBUNTU_DEEP_LEARNING_IMAGE_ID \
    --security-groups agile_data_science \
    --key-name agile_data_science \
    --instance-type g2.8xlarge \
    --count 1 \
| jq .ReservationId | tr -d '"' > .deep_reservation_id

RESERVATION_ID=`cat ./.deep_reservation_id`
echo "Got reservation ID '$RESERVATION_ID' ..."

# Use the ReservationId to get the public hostname to ssh to
echo ""
echo "Sleeping 10 seconds before inquiring to get the public hostname of the instance we just created ..."
sleep 5
echo "..."
sleep 5
echo "Awake!"
echo ""
echo "Using the reservation ID to get the public hostname ..."
INSTANCE_PUBLIC_HOSTNAME=`aws ec2 describe-instances | jq -c ".Reservations[] | select(.ReservationId | contains(\"$RESERVATION_ID\"))| .Instances[0].PublicDnsName" | tr -d '"'`

echo "The public hostname of the instance we just created is '$INSTANCE_PUBLIC_HOSTNAME' ..."
echo "Writing hostname to '.ec2_hostname' ..."
echo $INSTANCE_PUBLIC_HOSTNAME > .ec2_deep_hostname
echo ""

echo "Now we will tag this ec2 instance and name it 'agile_data_science_deep_ec2' ..."
INSTANCE_ID=`aws ec2 describe-instances | jq -c ".Reservations[] | select(.ReservationId | contains(\"$RESERVATION_ID\"))| .Instances[0].InstanceId" | tr -d '"'`
aws ec2 create-tags --resources $INSTANCE_ID --tags Key=Name,Value=agile_data_science_deep_ec2
echo ""

echo "After a few minutes (for it to initialize), you may ssh to this machine via the command in red: "
# Make the ssh instructions red
RED='\033[0;31m'
NC='\033[0m' # No Color
echo -e "${RED}ssh -i ./agile_data_science.pem ubuntu@$INSTANCE_PUBLIC_HOSTNAME${NC}"
echo "Note: only your IP of '$EXTERNAL_IP' is authorized to connect to this machine."
echo ""
echo "NOTE: IT WILL TAKE SEVERAL MINUTES FOR THIS MACHINE TO INITIALIZE. PLEASE WAIT FIVE MINUTES BEFORE LOGGING IN."
echo ""
echo "Note: if you ssh to this machine after a few minutes and there is no software in \$HOME, please wait a few minutes for the install to finish."

echo ""
echo "Once you ssh in, the exercise code is in the Agile_Data_Code_2 directory! Run all files from this directory, with the exception of the web applications, which you will run from ex. ch08/web"

echo ""
echo "Note: after a few minutes, now you will need to run ./ec2_create_tunnel.sh to forward ports 5000 and 8888 on the ec2 instance to your local ports 5000 and 8888. This way you can run the example web applications on the ec2 instance and browse them at http://localhost:5000 and you can view Jupyter notebooks at http://localhost:8888"
echo "If you tire of the ssh tunnel port forwarding, you may end these connections by executing ./ec2_kill_tunnel.sh"
echo ""
echo "---------------------------------------------------------------------------------------------------------------------"
echo ""
echo "Thanks for trying Agile Data Science 2.0!"
echo ""
echo "If you have ANY problems, please file an issue on Github at https://github.com/rjurney/Agile_Data_Code_2/issues and I will resolve them."
echo ""
echo "If you need help creating your own applications, or with on-site or video training..."
echo "Check out Data Syndrome at http://datasyndrome.com"
echo ""
echo "Enjoy! Russell Jurney <@rjurney> <russell.jurney@gmail.com> <http://linkedin.com/in/russelljurney>"
echo ""
