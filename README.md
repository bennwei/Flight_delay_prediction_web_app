# Flight_delay_prediction_web_app

Code for a big data web application to predict USA airline traffic delay with Python, Flask, Apache Spark, Kafka, MongoDB, ElasticSearch, d3.js, scikit-learn, MLlib and Apache Airflow.
For this project, I followed the book Agile data science 2.0 (by Russell Jurney) to learn how to build and implement a complete data science product from front-end to back-end. In this project,
I also review all the codes, identify and fix some bugs to make some parts of the app working as expected.

## Installation

### Vagrant/Virtualbox Install

Installation takes a few minutes, using Vagrant and Virtualbox. 

**Note: Vagrant/Virtualbox method requires 9GB free RAM, which will mean closing most programs on a 16GB Macbook Pro. If you don't close most everything, you will run out of RAM and your system will crash. Use the EC2 method if this is a problem for you.**

```
vagrant up
vagrant ssh
```

## Running Examples

All scripts run from the base directory, except the web app which runs in ex. `ch08/web/`.

# The Data Value Pyramid

We follow Data Value Pyramid (Originally by Pete Warden) when building this web app:

![Data Value Pyramid](images/climbing_the_pyramid_chapter_intro.png)

# System Architecture

The following diagrams express the basic concepts in the system architecture. The front and back end architectures work together to make a complete predictive system.

## Front End Architecture

This diagram shows how the front end architecture works in our flight delay prediction application. The user fills out a form with some basic information in a form on a web page, which is submitted to the server. The server fills out some neccesary fields derived from those in the form like "day of year" and emits a Kafka message containing a prediction request. Spark Streaming is listening on a Kafka queue for these requests, and makes the prediction, storing the result in MongoDB. Meanwhile, the client has received a UUID in the form's response, and has been polling another endpoint every second. Once the data is available in Mongo, the client's next request picks it up. Finally, the client displays the result of the prediction to the user! 

This setup is extremely fun to setup, operate and watch. Check out chapters 7 and 8 for more information!

![Front End Architecture](images/front_end_realtime_architecture.png)

## Back End Architecture

The back end architecture diagram shows how we train a classifier model using historical data (all flights from 2015) on disk (HDFS or Amazon S3, etc.) to predict flight delays in batch in Spark. We save the model to disk when it is ready. Next, we launch Zookeeper and a Kafka queue. We use Spark Streaming to load the classifier model, and then listen for prediction requests in a Kafka queue. When a prediction request arrives, Spark Streaming makes the prediction, storing the result in MongoDB where the web application can pick it up.

This architecture is extremely powerful, and it is a huge benefit that we get to use the same code in batch and in realtime with PySpark Streaming.

![Backend Architecture](images/back_end_realtime_architecture.png)

# Screenshots

Below are some examples of parts of the application we build in this book and in this repo. Check out the book for more!

## Airline Entity Page

Each airline gets its own entity page, complete with a summary of its fleet and a description pulled from Wikipedia.

![Airline Page](images/airline_page_enriched_wikipedia.png)

## Airplane Fleet Page

We demonstrate summarizing an entity with an airplane fleet page which describes the entire fleet.

![Airplane Fleet Page](images/airplanes_page_chart_v1_v2.png)

## Flight Delay Prediction UI

We create an entire realtime predictive system with a web front-end to submit prediction requests.

![Predicting Flight Delays UI](images/predicting_flight_kafka_waiting.png)
