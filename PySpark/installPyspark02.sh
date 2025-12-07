#!/bin/sh

# Not working

# PySpark Installation Script for Chainguard Alpine with Native Packages
# Uses openjdk17-jre + pyspark pip (Java 17 confirmed available)

set -e  # Exit on any error


echo "=== Updating Chainguard packages ==="
apk update

echo "=== Installing Java 17, Python 3, pip + essentials ==="
apk add --no-cache \
    # openjdk17-jre \
	openjdk-17-jre \
    python3 \
    py3-pip \
    curl \
    bash \
    && ln -sf /usr/bin/python3 /usr/bin/python

echo "=== Installing PySpark via pip ==="
pip3 install --no-cache-dir --root-user-action=ignore pyspark==4.0.1

echo "=== Setting up environment variables ==="
mkdir -p /etc/profile.d
cat > /etc/profile.d/pyspark.sh << 'EOF'
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk/jre
export PATH=$JAVA_HOME/bin:$PATH
EOF

# export SPARK_HOME=/usr/lib/python3.*/site-packages/pyspark
# export PYSPARK_PYTHON=python3

# Source for current shell
. /etc/profile.d/pyspark.sh

echo "=== Verifying installation ==="
echo "Java version:"
java -version
echo "Python version:"
python3 --version
echo "PySpark version:"
python3 -c "import pyspark; print('PySpark', pyspark.__version__)"

echo "=== Testing PySpark SparkSession ==="
python3 -c "
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName('test').master('local[*]').getOrCreate()
df = spark.range(5).toDF('number')
print('✅ PySpark working!')
df.show()
spark.stop()
print('Test PASSED!')
"

echo "=== Installation complete! ==="
echo "Run: source /etc/profile.d/pyspark.sh"
echo "Test: pyspark  or  python3 -c \"from pyspark.sql import SparkSession; spark=SparkSession.builder.getOrCreate();spark.stop()\""



# /root/ProjectRpi/Rpi/PersonalAssistant/PySpark
# 2782395ac104:~/ProjectRpi/Rpi/PersonalAssistant/PySpark# ap
# k add openjdk-17-jre
# apk add --no-cache gcompat libc6-compat libgcc
# apk add gcompat libc6-compat libgcc
# export LD_PRELOAD=/usr/lib/libgomp.so.1
# apk update
# apk add --no-cache libstdc++ musl-locales gcc gcompat-symbol-hacks
# apk add libstdc++ musl-locales gcc gcompat-symbol-hacks

