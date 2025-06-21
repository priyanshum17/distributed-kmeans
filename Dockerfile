FROM bitnami/spark:latest

# Switch to root to fix permissions
USER root

# Ensure /opt/bitnami/spark/tmp exists and is writable by UID 1001
RUN echo "spark:x:1001:1001:Spark:/home/spark:/sbin/nologin" >> /etc/passwd

# Create the Spark user and group if they do not exist
RUN mkdir -p /opt/bitnami/spark/tmp && \
    chown -R 1001:1001 /opt/bitnami/spark/tmp

# Install additional Python packages
RUN pip install numpy pandas

# Switch back to the default Bitnami Spark user
USER 1001
WORKDIR /opt/bitnami/spark
