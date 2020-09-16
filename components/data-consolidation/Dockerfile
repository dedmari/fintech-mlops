FROM muneer7589/kaggle-dataset-download

# Directory for src code
# RUN mkdir /workdir

# Install Kaggle package
# RUN pip3 install kaggle

# Copy source code to docker image
COPY components/data-consolidation/src/download_kaggle_dataset.py /workdir

# Change working directory to app
WORKDIR /workdir