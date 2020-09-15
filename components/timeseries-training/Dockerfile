FROM tensorflow/tensorflow:1.15.0-py3

# Install dependencies
RUN pip install pandas

# Directory for src code
RUN mkdir /workdir

# Copy source code to docker image
COPY src/timeseries_training.py /workdir

# Change working directory to app
WORKDIR /workdir