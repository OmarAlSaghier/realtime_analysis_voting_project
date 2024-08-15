#!/bin/bash

# Install Python dependencies
pip install -r /opt/bitnami/spark/requirements.txt

# Start the Spark master
exec bin/spark-class org.apache.spark.deploy.master.Master
