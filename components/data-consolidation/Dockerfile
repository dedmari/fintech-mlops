FROM tensorflow/tensorflow:1.15.0-py3

# Directory for src code
RUN mkdir /workdir

# Install Kaggle package
RUN pip3 install kaggle

# Copy source code to docker image
COPY src/download_kaggle_dataset.py /workdir

# Change working directory to app
WORKDIR /workdir