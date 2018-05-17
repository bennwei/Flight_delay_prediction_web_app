#!/usr/bin/env bash

sudo chown -R vagrant /home/vagrant
sudo chgrp -R vagrant /home/vagrant

#
# Update & install dependencies
#
sudo apt-get update
sudo apt-get install -y zip unzip curl bzip2 python-dev build-essential git libssl1.0.0 libssl-dev \
    software-properties-common debconf-utils python-software-properties

#
# Install Java and setup ENV
#
sudo add-apt-repository -y ppa:webupd8team/java
sudo apt-get update
echo "oracle-java8-installer shared/accepted-oracle-license-v1-1 select true" | sudo debconf-set-selections
sudo apt-get install -y oracle-java8-installer oracle-java8-set-default

export JAVA_HOME=/usr/lib/jvm/java-8-oracle
echo "export JAVA_HOME=/usr/lib/jvm/java-8-oracle" | sudo tee -a /home/vagrant/.bash_profile

#
# Install Miniconda
#
echo "curl -sLko /tmp/Miniconda3-latest-Linux-x86_64.sh https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh"
curl -sLko /tmp/Miniconda3-latest-Linux-x86_64.sh https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
chmod +x /tmp/Miniconda3-latest-Linux-x86_64.sh
/tmp/Miniconda3-latest-Linux-x86_64.sh -b -p /home/vagrant/anaconda

export PATH=/home/vagrant/anaconda/bin:$PATH
echo 'export PATH=/home/vagrant/anaconda/bin:$PATH' | sudo tee -a /home/vagrant/.bash_profile

sudo chown -R vagrant /home/vagrant/anaconda
sudo chgrp -R vagrant /home/vagrant/anaconda

#sudo apt-get install -y python3 python3-dev python3-numpy python3-scipy python3-setuptools
#sudo easy_install3 pip

#
# Install Clone repo, install Python dependencies
#
cd /home/vagrant
git clone https://github.com/rjurney/Agile_Data_Code_2
cd /home/vagrant/Agile_Data_Code_2
export PROJECT_HOME=/home/vagrant/Agile_Data_Code_2
echo "export PROJECT_HOME=/home/vagrant/Agile_Data_Code_2" | sudo tee -a /home/vagrant/.bash_profile
conda install python=3.5
conda install iso8601 numpy scipy scikit-learn matplotlib ipython jupyter
pip install bs4 Flask beautifulsoup4 airflow frozendict geopy kafka-python py4j pymongo pyelasticsearch requests selenium tabulate tldextract wikipedia findspark
sudo chown -R vagrant /home/vagrant/Agile_Data_Code_2
sudo chgrp -R vagrant /home/vagrant/Agile_Data_Code_2
cd /home/vagrant

#
# Install Hadoop
#
echo "curl -sLko /tmp/hadoop-2.7.3.tar.gz http://apache.osuosl.org/hadoop/common/hadoop-2.7.3/hadoop-2.7.3.tar.gz"
curl -sLko /tmp/hadoop-2.7.3.tar.gz http://apache.osuosl.org/hadoop/common/hadoop-2.7.3/hadoop-2.7.3.tar.gz
mkdir -p /home/vagrant/hadoop
cd /home/vagrant/
tar -xvf /tmp/hadoop-2.7.3.tar.gz -C hadoop --strip-components=1

echo '# Hadoop environment setup' | sudo tee -a /home/vagrant/.bash_profile
export HADOOP_HOME=/home/vagrant/hadoop
echo 'export HADOOP_HOME=/home/vagrant/hadoop' | sudo tee -a /home/vagrant/.bash_profile
export PATH=$PATH:$HADOOP_HOME/bin
echo 'export PATH=$PATH:$HADOOP_HOME/bin' | sudo tee -a /home/vagrant/.bash_profile
export HADOOP_CLASSPATH=$(hadoop classpath)
echo 'export HADOOP_CLASSPATH=$(hadoop classpath)' | sudo tee -a /home/vagrant/.bash_profile
export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
echo 'export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop' | sudo tee -a /home/vagrant/.bash_profile

# Give to vagrant
sudo chown -R vagrant /home/vagrant/hadoop
sudo chgrp -R vagrant /home/vagrant/hadoop

#
# Install Spark
#
echo "curl -sLko /tmp/spark-2.1.0-bin-without-hadoop.tgz http://d3kbcqa49mib13.cloudfront.net/spark-2.1.0-bin-without-hadoop.tgz"
curl -sLko /tmp/spark-2.1.0-bin-without-hadoop.tgz http://d3kbcqa49mib13.cloudfront.net/spark-2.1.0-bin-without-hadoop.tgz
mkdir -p /home/vagrant/spark
cd /home/vagrant
tar -xvf /tmp/spark-2.1.0-bin-without-hadoop.tgz -C spark --strip-components=1

echo "" >> /home/vagrant/.bash_profile
echo "# Spark environment setup" | sudo tee -a /home/vagrant/.bash_profile
export SPARK_HOME=/home/vagrant/spark
echo 'export SPARK_HOME=/home/vagrant/spark' | sudo tee -a /home/vagrant/.bash_profile
export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop/
echo 'export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop/' | sudo tee -a /home/vagrant/.bash_profile
export SPARK_DIST_CLASSPATH=`$HADOOP_HOME/bin/hadoop classpath`
echo 'export SPARK_DIST_CLASSPATH=`$HADOOP_HOME/bin/hadoop classpath`' | sudo tee -a /home/vagrant/.bash_profile
export PATH=$PATH:$SPARK_HOME/bin
echo 'export PATH=$PATH:$SPARK_HOME/bin' | sudo tee -a /home/vagrant/.bash_profile

# Have to set spark.io.compression.codec in Spark local mode
cp /home/vagrant/spark/conf/spark-defaults.conf.template /home/vagrant/spark/conf/spark-defaults.conf
echo 'spark.io.compression.codec org.apache.spark.io.SnappyCompressionCodec' | sudo tee -a /home/vagrant/spark/conf/spark-defaults.conf

# Give Spark 8GB of RAM, used Python3
echo "spark.driver.memory 9g" | sudo tee -a $SPARK_HOME/conf/spark-defaults.conf
echo "PYSPARK_PYTHON=python3" | sudo tee -a $SPARK_HOME/conf/spark-env.sh
echo "PYSPARK_DRIVER_PYTHON=python3" | sudo tee -a $SPARK_HOME/conf/spark-env.sh

# Setup log4j config to reduce logging output
cp $SPARK_HOME/conf/log4j.properties.template $SPARK_HOME/conf/log4j.properties
sed -i 's/INFO/ERROR/g' $SPARK_HOME/conf/log4j.properties

# Give to vagrant
sudo chown -R vagrant /home/vagrant/spark
sudo chgrp -R vagrant /home/vagrant/spark

#
# Install MongoDB and dependencies
#
#echo "deb [ arch=amd64,arm64 ] http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.4.list
#sudo apt-get update
#sudo apt-get install -y --allow-unauthenticated mongodb-org-shell mongodb-org-server mongodb-org-mongos mongodb-org-tools mongodb-org
sudo apt-get install -y mongodb
sudo mkdir -p /data/db
sudo chown -R mongodb /data/db
sudo chgrp -R mongodb /data/db

# run MongoDB as daemon
sudo /usr/bin/mongod --fork --logpath /var/log/mongodb.log

# Get the MongoDB Java Driver
echo "curl -sLko /home/vagrant/Agile_Data_Code_2/lib/mongo-java-driver-3.4.2.jar http://central.maven.org/maven2/org/mongodb/mongo-java-driver/3.4.2/mongo-java-driver-3.4.2.jar"
curl -sLko /home/vagrant/Agile_Data_Code_2/lib/mongo-java-driver-3.4.2.jar http://central.maven.org/maven2/org/mongodb/mongo-java-driver/3.4.2/mongo-java-driver-3.4.2.jar

# Install the mongo-hadoop project in the mongo-hadoop directory in the root of our project.
echo "curl -sLko /tmp/mongo-hadoop-r2.0.2.tar.gz https://github.com/mongodb/mongo-hadoop/archive/r2.0.2.tar.gz"
curl -sLko /tmp/mongo-hadoop-r2.0.2.tar.gz https://github.com/mongodb/mongo-hadoop/archive/r2.0.2.tar.gz
mkdir /home/vagrant/mongo-hadoop
cd /home/vagrant
tar -xvzf /tmp/mongo-hadoop-r2.0.2.tar.gz -C mongo-hadoop --strip-components=1
rm -rf /tmp/mongo-hadoop-r2.0.2.tar.gz

# Now build the mongo-hadoop-spark jars
cd /home/vagrant/mongo-hadoop
./gradlew jar
cp /home/vagrant/mongo-hadoop/spark/build/libs/mongo-hadoop-spark-*.jar /home/vagrant/Agile_Data_Code_2/lib/
cp /home/vagrant/mongo-hadoop/build/libs/mongo-hadoop-*.jar /home/vagrant/Agile_Data_Code_2/lib/
cd /home/vagrant

# Now build the pymongo_spark package
cd /home/vagrant/mongo-hadoop/spark/src/main/python
python setup.py install
cp /home/vagrant/mongo-hadoop/spark/src/main/python/pymongo_spark.py /home/vagrant/Agile_Data_Code_2/lib/
export PYTHONPATH=$PYTHONPATH:$PROJECT_HOME/lib
echo 'export PYTHONPATH=$PYTHONPATH:$PROJECT_HOME/lib' | sudo tee -a /home/vagrant/.bash_profile
cd /home/vagrant

rm -rf /home/vagrant/mongo-hadoop

#
# Install ElasticSearch in the elasticsearch directory in the root of our project, and the Elasticsearch for Hadoop package
#
echo "curl -sLko /tmp/elasticsearch-5.2.1.tar.gz https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-5.2.1.tar.gz"
curl -sLko /tmp/elasticsearch-5.2.1.tar.gz https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-5.2.1.tar.gz
mkdir /home/vagrant/elasticsearch
cd /home/vagrant
tar -xvzf /tmp/elasticsearch-5.2.1.tar.gz -C elasticsearch --strip-components=1
sudo chown -R vagrant /home/vagrant/elasticsearch
sudo chgrp -R vagrant /home/vagrant/elasticsearch
sudo mkdir -p /home/vagrant/elasticsearch/logs
sudo chown -R vagrant /home/vagrant/elasticsearch/logs
sudo chgrp -R vagrant /home/vagrant/elasticsearch/logs

# Run elasticsearch
sudo -u vagrant /home/vagrant/elasticsearch/bin/elasticsearch -d # re-run if you shutdown your computer

# Run a query to test - it will error but should return json
echo "Testing Elasticsearch with a query ..." | tee -a $LOG_FILE
curl 'localhost:9200/agile_data_science/on_time_performance/_search?q=Origin:ATL&pretty'

# Install Elasticsearch for Hadoop
echo "curl -sLko /tmp/elasticsearch-hadoop-5.2.1.zip http://download.elastic.co/hadoop/elasticsearch-hadoop-5.2.1.zip"
curl -sLko /tmp/elasticsearch-hadoop-5.2.1.zip http://download.elastic.co/hadoop/elasticsearch-hadoop-5.2.1.zip
unzip /tmp/elasticsearch-hadoop-5.2.1.zip
mv /home/vagrant/elasticsearch-hadoop-5.2.1 /home/vagrant/elasticsearch-hadoop
cp /home/vagrant/elasticsearch-hadoop/dist/elasticsearch-hadoop-5.2.1.jar /home/vagrant/Agile_Data_Code_2/lib/
cp /home/vagrant/elasticsearch-hadoop/dist/elasticsearch-spark-20_2.10-5.2.1.jar /home/vagrant/Agile_Data_Code_2/lib/
echo "spark.speculation false" | sudo tee -a /home/vagrant/spark/conf/spark-defaults.conf
rm -f /tmp/elasticsearch-hadoop-5.2.1.zip
rm -rf /home/vagrant/elasticsearch-hadoop/conf/spark-defaults.conf

#
# Spark jar setup
#

# Install and add snappy-java and lzo-java to our classpath below via spark.jars
cd /home/vagrant/Agile_Data_Code_2
echo "curl -sLko lib/snappy-java-1.1.2.6.jar http://central.maven.org/maven2/org/xerial/snappy/snappy-java/1.1.2.6/snappy-java-1.1.2.6.jar"
curl -sLko lib/snappy-java-1.1.2.6.jar http://central.maven.org/maven2/org/xerial/snappy/snappy-java/1.1.2.6/snappy-java-1.1.2.6.jar
echo "curl -sLko lib/lzo-hadoop-1.0.5.jar http://central.maven.org/maven2/org/anarres/lzo/lzo-hadoop/1.0.0/lzo-hadoop-1.0.0.jar"
curl -sLko lib/lzo-hadoop-1.0.5.jar http://central.maven.org/maven2/org/anarres/lzo/lzo-hadoop/1.0.0/lzo-hadoop-1.0.0.jar
cd /home/vagrant

# Set the spark.jars path
echo "spark.jars /home/vagrant/Agile_Data_Code_2/lib/mongo-hadoop-spark-2.0.2.jar,/home/vagrant/Agile_Data_Code_2/lib/mongo-java-driver-3.4.2.jar,/home/vagrant/Agile_Data_Code_2/lib/mongo-hadoop-2.0.2.jar,/home/vagrant/Agile_Data_Code_2/lib/elasticsearch-spark-20_2.10-5.2.1.jar,/home/vagrant/Agile_Data_Code_2/lib/snappy-java-1.1.2.6.jar,/home/vagrant/Agile_Data_Code_2/lib/lzo-hadoop-1.0.5.jar" | sudo tee -a /home/vagrant/spark/conf/spark-defaults.conf

#
# Kafka install and setup
#
echo "curl -sLko /tmp/kafka_2.11-0.10.1.1.tgz http://www-us.apache.org/dist/kafka/0.10.1.1/kafka_2.11-0.10.1.1.tgz"
curl -sLko /tmp/kafka_2.11-0.10.1.1.tgz http://www-us.apache.org/dist/kafka/0.10.1.1/kafka_2.11-0.10.1.1.tgz
mkdir -p /home/vagrant/kafka
cd /home/vagrant/
tar -xvzf /tmp/kafka_2.11-0.10.1.1.tgz -C kafka --strip-components=1 && rm -f /tmp/kafka_2.11-0.10.1.1.tgz
rm -f /tmp/kafka_2.11-0.10.1.1.tgz

# Set the log dir to kafka/logs
sed -i '/log.dirs=\/tmp\/kafka-logs/c\log.dirs=logs' /home/vagrant/kafka/config/server.properties

# Give to vagrant
sudo chown -R vagrant /home/vagrant/kafka
sudo chgrp -R vagrant /home/vagrant/kafka

# Run zookeeper (which kafka depends on), then Kafka
sudo -H -u vagrant /home/vagrant/kafka/bin/zookeeper-server-start.sh -daemon /home/vagrant/kafka/config/zookeeper.properties
sudo -H -u vagrant /home/vagrant/kafka/bin/kafka-server-start.sh -daemon /home/vagrant/kafka/config/server.properties

#
# Install and setup Airflow
#
pip install airflow[hive]

mkdir /home/vagrant/airflow
mkdir /home/vagrant/airflow/dags
mkdir /home/vagrant/airflow/logs
mkdir /home/vagrant/airflow/plugins

sudo chown -R vagrant /home/vagrant/airflow
sudo chgrp -R vagrant /home/vagrant/airflow

airflow initdb
airflow webserver -D &
airflow scheduler -D &

# Install Apache Zeppelin
echo "curl -sLko /tmp/zeppelin-0.7.0-bin-all.tgz http://www-us.apache.org/dist/zeppelin/zeppelin-0.7.0/zeppelin-0.7.0-bin-all.tgz"
curl -sLko /tmp/zeppelin-0.7.0-bin-all.tgz http://www-us.apache.org/dist/zeppelin/zeppelin-0.7.0/zeppelin-0.7.0-bin-all.tgz
mkdir zeppelin
tar -xvzf /tmp/zeppelin-0.7.0-bin-all.tgz -C zeppelin --strip-components=1

# Configure Zeppelin
cp zeppelin/conf/zeppelin-env.sh.template zeppelin/conf/zeppelin-env.sh
echo "export SPARK_HOME=$PROJECT_HOME/spark" >> zeppelin/conf/zeppelin-env.sh
echo "export SPARK_MASTER=local" >> zeppelin/conf/zeppelin-env.sh
echo "export SPARK_CLASSPATH=" >> zeppelin/conf/zeppelin-env.sh

# Jupyter server setup
jupyter notebook --generate-config
cp /home/vagrant/Agile_Data_Code_2/jupyter_notebook_config.py /home/vagrant/.jupyter/
mkdir /home/vagrant/certs
sudo openssl req -x509 -nodes -days 365 -newkey rsa:1024 -subj "/C=US" -keyout /home/vagrant/certs/mycert.pem -out /home/vagrant/certs/mycert.pem

jupyter notebook --ip=0.0.0.0 --allow-root --no-browser &

#
# Cleanup
#
sudo apt-get clean
sudo rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

echo "DONE!"
