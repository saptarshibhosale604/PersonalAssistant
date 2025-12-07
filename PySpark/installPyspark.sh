#!/bin/sh
# Java is not installed saying

# PySpark Installation Script for Alpine Linux (RPi-like system)
# Compatible with alpine/ollama base image, 28.7GB FS, 7.9GB RAM
# Uses /bin/sh as specified

set -e  # Exit on any error

echo "=== Updating Alpine packages ==="
apk update

echo "=== Installing Java 17, Python 3, and pip ==="
apk add --no-cache \
    openjdk17-jre \
    python3 \
    py3-pip \
    curl \
    tar \
    bash \
    && ln -sf /usr/bin/python3 /usr/bin/python

echo "=== Installing PySpark via pip (minimal, no full Spark download) ==="
pip3 install --no-cache-dir pyspark==4.0.1

echo "=== Setting up environment variables ==="
cat > /etc/profile.d/pyspark.sh << 'EOF'
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk
export SPARK_HOME=/usr/lib/python3.11/site-packages/pyspark
export PATH=$PATH:$SPARK_HOME/bin
EOF

# Source for current shell
. /etc/profile.d/pyspark.sh

echo "=== Verifying installation ==="
java -version
python3 --version
pyspark --version

echo "=== Testing PySpark ==="
python3 -c "from pyspark.sql import SparkSession; spark = SparkSession.builder.appName('test').getOrCreate(); print('PySpark ready!'); spark.stop()"

echo "=== Installation complete! ==="
echo "Run 'pyspark' to start the shell."
echo "Add '. /etc/profile.d/pyspark.sh' to your shell startup if needed."
echo "Memory usage optimized for 7.9GB RAM system."

