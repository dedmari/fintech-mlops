
FROM muneer7589/timeseries-preprocess-data

# Install dependencies
# RUN pip3 install pandas

# Directory for src code
# RUN mkdir /workdir

# Copy source code to docker image
COPY components/timeseries-preprocessing/src/preprocess_data.py /workdir

# Change working directory to app
WORKDIR /workdir
