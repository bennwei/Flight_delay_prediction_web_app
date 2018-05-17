#!/usr/bin/env bash
#
# This file is intended as a guide to installation, and not a complete script that will work on all platforms.
# Use accordingly. I think it works, though. The only things installed to your OS outside this directory are
# Anaconda plus a few additions to ~/.bash_profile. Everything else is self contained.
#

#
# Lots of stuff depends on $PROJECT_HOME being set
#
export PROJECT_HOME=`pwd`
echo "export PROJECT_HOME=$PROJECT_HOME" >> ~/.bash_profile

#
# Check if Java is installed and halt if not
#
#if [ -z `which java` ]; then
#  echo "ERROR: JAVA IS REQUIRED TO CONTINUE INSTALL!"
#  echo "Please install Java, which you can find at https://www.java.com/en/download/help/download_options.xml"
#  exit;
#else
#  echo "Java detected, continuing install..."
#fi

#
# Make backup of ~/.bash_profile
#
echo "Backing up ~/.bash_profile to ~/.bash_profile.agile_data_science.bak"
cp ~/.bash_profile ~/.bash_profile.agile_data_science.bak

#
# Define the right url for Anaconda and Mongo
#
if [ "$(uname)" == "Darwin" ]; then
    ANADONCA_OS_NAME='MacOSX'
    MONGO_FILENAME='mongodb-osx-x86_64-3.4.1.tgz'
    MONGO_DOWNLOAD_URL='https://fastdl.mongodb.org/osx/mongodb-osx-x86_64-3.4.2.tgz'
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    ANADONCA_OS_NAME='Linux'
    MONGO_FILENAME='mongodb-linux-x86_64-amazon-3.4.1.tgz'
    MONGO_DOWNLOAD_URL='https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-amazon-3.4.2.tgz'
elif [ "$(expr substr $(uname -s) 1 10)" == "MINGW32_NT" ]; then
    ANADONCA_OS_NAME='Windows'
    MONGO_FILENAME='mongodb-win32-x86_64-3.4.1-signed.msi'
    MONGO_DOWNLOAD_URL='http://downloads.mongodb.org/win32/mongodb-win32-x86_64-2008plus-ssl-3.4.2-signed.msi'
fi

#
# Download and install Anaconda Python
#

# Only install Anaconda if it isn't already there
#if [ ! -d $HOME/anaconda ]; then
#  echo "Anaconda not found, installing to $HOME/anaconda ..."
#  curl -Lko "/tmp/Anaconda3-4.2.0-${ANADONCA_OS_NAME}-x86_64.sh" "http://repo.continuum.io/archive/Anaconda3-4.2.0-${ANADONCA_OS_NAME}-x86_64.sh"
#  bash "/tmp/Anaconda3-4.2.0-${ANADONCA_OS_NAME}-x86_64.sh" -b -p $HOME/anaconda
#  export PATH="$HOME/anaconda/bin:$PATH"
#  echo 'export PATH="$HOME/anaconda/bin:$PATH"' >> ~/.bash_profile
#else
#  echo "Skipping Anaconda, already installed..."
#fi

#
# Install dependencies
#

# Spark don't work with python 3.6
#echo "Downgrading Anaconda Python from 3.6 to 3.5, as 3.6 doesn't work with Spark 2.1.0 ..."
#conda install python=3.5

#echo "Installing Python libraries..."
# Install as many requirements as we can with conda
# conda install iso8601 numpy scipy scikit-learn matplotlib ipython jupyter
# Setup remaining Python package requirements
#pip install -r requirements.txt

#
# Install Hadoop in the hadoop directory in the root of our project. Also, setup
# our Hadoop environment for Spark to run
#
if [ ! -d hadoop ]; then
  echo "Installing hadoop 2.7.3 into $PROJECT_HOME/hadoop ..."

  # May need to update this link... see http://hadoop.apache.org/releases.html
  curl -Lko /tmp/hadoop-2.7.3.tar.gz http://ftp.wayne.edu/apache/hadoop/common/hadoop-2.7.3/hadoop-2.7.3.tar.gz

  mkdir hadoop
  tar -xvf /tmp/hadoop-2.7.3.tar.gz -C hadoop --strip-components=1
  echo '# Hadoop environment setup' >> ~/.bash_profile
  export HADOOP_HOME=$PROJECT_HOME/hadoop
  echo 'export HADOOP_HOME=$PROJECT_HOME/hadoop' >> ~/.bash_profile
  export PATH=$PATH:$HADOOP_HOME/bin
  echo 'export PATH=$PATH:$HADOOP_HOME/bin' >> ~/.bash_profile
  export HADOOP_CLASSPATH=$(hadoop classpath)
  echo 'export HADOOP_CLASSPATH=$(hadoop classpath)' >> ~/.bash_profile
  export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
  echo 'export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop' >> ~/.bash_profile
else
  echo "Hadoop already installed, skipping Hadoop..."
fi

#
# Install Spark in the spark directory in the root of our project. Also, setup
# our Spark environment for PySpark to run
#
if [ ! -d spark ]; then
  echo "Installing Spark 2.1.0 into $PROJECT_HOME/spark ..."

  # May need to update this link... see http://spark.apache.org/downloads.html
  curl -Lko /tmp/spark-2.1.0-bin-without-hadoop.tgz http://d3kbcqa49mib13.cloudfront.net/spark-2.1.0-bin-without-hadoop.tgz

  mkdir spark
  tar -xvf /tmp/spark-2.1.0-bin-without-hadoop.tgz -C spark --strip-components=1
  echo "" >> ~/.bash_profile
  echo "# Spark environment setup" >> ~/.bash_profile
  export SPARK_HOME=$PROJECT_HOME/spark
  echo 'export SPARK_HOME=$PROJECT_HOME/spark' >> ~/.bash_profile
  export HADOOP_CONF_DIR=$PROJECT_HOME/hadoop/etc/hadoop/
  echo 'export HADOOP_CONF_DIR=$PROJECT_HOME/hadoop/etc/hadoop/' >> ~/.bash_profile
  export SPARK_DIST_CLASSPATH=`$HADOOP_HOME/bin/hadoop classpath`
  echo 'export SPARK_DIST_CLASSPATH=`$HADOOP_HOME/bin/hadoop classpath`' >> ~/.bash_profile
  export PATH=$PATH:$SPARK_HOME/bin
  echo 'export PATH=$PATH:$SPARK_HOME/bin' >> ~/.bash_profile

  # Have to set spark.io.compression.codec in Spark local mode
  cp spark/conf/spark-defaults.conf.template spark/conf/spark-defaults.conf
  echo 'spark.io.compression.codec org.apache.spark.io.SnappyCompressionCodec' >> spark/conf/spark-defaults.conf

  # Give Spark 8GB of RAM
  echo "spark.driver.memory 8g" >> $SPARK_HOME/conf/spark-defaults.conf

  echo "PYSPARK_PYTHON=python3" >> $SPARK_HOME/conf/spark-env.sh
  echo "PYSPARK_DRIVER_PYTHON=python3" >> $SPARK_HOME/conf/spark-env.sh

  # Setup log4j config to reduce logging output
  cp $SPARK_HOME/conf/log4j.properties.template $SPARK_HOME/conf/log4j.properties
  sed -i .bak 's/INFO/ERROR/g' $SPARK_HOME/conf/log4j.properties
else
  echo "Spark already installed, skipping Spark..."
fi

#
# Install MongoDB in the mongo directory in the root of our project. Also, get the jar for the MongoDB driver
# and the mongo-hadoop project.
#

# Only install if mongod isn't on the path and there is no mongodb directory
if [ -z `which mongod` ] && [ ! -d mongodb ]; then
  echo "Installing MongoDB to $PROJECT_HOME/mongodb ..."

  curl -Lko /tmp/$MONGO_FILENAME $MONGO_DOWNLOAD_URL
  mkdir mongodb
  tar -xvf /tmp/$MONGO_FILENAME -C mongodb --strip-components=1
  export PATH=$PATH:$PROJECT_HOME/mongodb/bin
  echo 'export PATH=$PATH:$PROJECT_HOME/mongodb/bin' >> ~/.bash_profile
  mkdir -p mongodb/data/db

  # Start Mongo
  mongodb/bin/mongod --dbpath mongodb/data/db & # re-run if you shutdown your computer
else
  echo "Skipping MongoDB, already installed..."
fi

# Get the MongoDB Java Driver
echo "Fetching the MongoDB Java Driver to $PROJECT_HOME/lib/ ..."
curl -Lko lib/mongo-java-driver-3.4.0.jar http://central.maven.org/maven2/org/mongodb/mongo-java-driver/3.4.0/mongo-java-driver-3.4.0.jar

# Install the mongo-hadoop project in the mongo-hadoop directory in the root of our project.
echo "Installing the mongo-hadoop project in $PROJECT_HOME/mongo-hadoop ..."
curl -Lko /tmp/mongo-hadoop-r2.0.2.tar.gz https://github.com/mongodb/mongo-hadoop/archive/r2.0.2.tar.gz
mkdir mongo-hadoop
tar -xvzf /tmp/mongo-hadoop-r2.0.2.tar.gz -C mongo-hadoop --strip-components=1

# Now build the mongo-hadoop-spark jars
echo "Building mongo-hadoop..."
cd mongo-hadoop
./gradlew jar
cd ..
cp mongo-hadoop/spark/build/libs/mongo-hadoop-spark-*.jar lib/
cp mongo-hadoop/build/libs/mongo-hadoop-*.jar lib/

# Now build the pymongo_spark package
# pip install py4j # add sudo if needed
# pip install pymongo # add sudo if needed
# pip install pymongo-spark # add sudo if needed
cd mongo-hadoop/spark/src/main/python
python setup.py install
cd $PROJECT_HOME# to $PROJECT_HOME
cp mongo-hadoop/spark/src/main/python/pymongo_spark.py lib/
export PYTHONPATH=$PYTHONPATH:$PROJECT_HOME/lib
echo 'export PYTHONPATH=$PYTHONPATH:$PROJECT_HOME/lib' >> ~/.bash_profile

#
# Install ElasticSearch in the elasticsearch directory in the root of our project, and the Elasticsearch for Hadoop package
#
if [ -z `which elasticsearch` ] && [ ! -d elasticsearch ]; then
  echo "Installing elasticsearch to $PROJECT_HOME/elasticsearch ..."

  curl -Lko /tmp/elasticsearch-5.1.1.tar.gz https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-5.1.1.tar.gz
  mkdir elasticsearch
  tar -xvzf /tmp/elasticsearch-5.1.1.tar.gz -C elasticsearch --strip-components=1

  # Run elasticsearch
  elasticsearch/bin/elasticsearch -d # re-run if you shutdown your computer
else
  echo "Skipping elasticsearch, already installed..."
fi

# Install Elasticsearch for Hadoop
echo "Installing elasticsearch-hadoop to $PROJECT_HOME/elasticsearch-hadoop ..."
curl -Lko /tmp/elasticsearch-hadoop-5.0.0-alpha5.zip http://download.elastic.co/hadoop/elasticsearch-hadoop-5.0.0-alpha5.zip
unzip /tmp/elasticsearch-hadoop-5.0.0-alpha5.zip
mv elasticsearch-hadoop-5.0.0-alpha5 elasticsearch-hadoop
cp elasticsearch-hadoop/dist/elasticsearch-hadoop-5.0.0-alpha5.jar lib/
cp elasticsearch-hadoop/dist/elasticsearch-spark-20_2.10-5.0.0-alpha5.jar lib/
echo "spark.speculation false" >> $PROJECT_HOME/spark/conf/spark-defaults.conf

# Install and add snappy-java and lzo-java to our classpath below via spark.jars
echo "Installing snappy-java and lzo-hadoop to $PROJECT_HOME/lib ..."
curl -Lko lib/snappy-java-1.1.2.6.jar http://central.maven.org/maven2/org/xerial/snappy/snappy-java/1.1.2.6/snappy-java-1.1.2.6.jar
curl -Lko lib/lzo-hadoop-1.0.5.jar http://central.maven.org/maven2/org/anarres/lzo/lzo-hadoop/1.0.0/lzo-hadoop-1.0.0.jar

# Setup mongo and elasticsearch jars for Spark
echo "spark.jars $PROJECT_HOME/lib/mongo-hadoop-spark-2.0.0-rc0.jar,\
$PROJECT_HOME/lib/mongo-java-driver-3.2.2.jar,\
$PROJECT_HOME/lib/mongo-hadoop-2.0.0-rc0.jar,\
$PROJECT_HOME/lib/elasticsearch-spark-20_2.10-5.0.0-alpha5.jar,\
$PROJECT_HOME/lib/snappy-java-1.1.2.6.jar,\
$PROJECT_HOME/lib/lzo-hadoop-1.0.0.jar" \
  >> spark/conf/spark-defaults.conf

# Setup spark classpath for snappy for parquet... required for OS X 10.11, others can skip
echo "SPARK_CLASSPATH=$PROJECT_HOME/lib/snappy-java-1.1.2.6.jar" >> spark/conf/spark-env.sh

#
# Install Apache Kafka and dependencies
#

# Install Kafka
if [ -z `which kafka-server-start.sh` ] && [ ! -d kafka ]; then
  echo "Installing kafka 2.11-0.10.1.1 to $PROJECT_HOME/kafka ..."
  curl -Lko /tmp/kafka_2.11-0.10.1.1.tgz http://www-us.apache.org/dist/kafka/0.10.1.1/kafka_2.11-0.10.1.1.tgz
  mkdir kafka
  tar -xvzf /tmp/kafka_2.11-0.10.1.1.tgz -C kafka --strip-components=1
else
  echo "Skipping kafka, already installed..."
fi

# Run kafka

# Install Apache Incubating Airflow
if [ -z `which airflow` ]; then
  pip install airflow
  mkdir ~/airflow
  mkdir ~/airflow/dags
  mkdir ~/airflow/logs
  mkdir ~/airflow/plugins
  airflow initdb
  airflow webserver -D
fi
