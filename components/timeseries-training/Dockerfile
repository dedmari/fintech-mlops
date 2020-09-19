FROM muneer7589/timeseries-train

# Install dependencies
#RUN pip3 install pandas

# Directory for src code
# RUN mkdir /workdir

# Copy source code to docker image
COPY components/timeseries-training/src/timeseries_training.py /workdir

# Change working directory to app
WORKDIR /workdir