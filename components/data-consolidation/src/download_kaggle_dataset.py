import os
from zipfile import ZipFile
import argparse

def download_dataset_from_kaggle(
        dataset_name = 'szrlee/stock-time-series-20050101-to-20171231',
        download_dir = 'djia_30_stock_data/',
        parent_dir = '/mnt/data/'
):
    """
    Downloads Kaggle dataset and store data at download_dir under parent_dir

    Args:
        dataset_name (str): Kaggle Dataset url/name
        download_dir (str): Directory where will be stored
        parent_dir (str): Parent directory or mount path

    """

    # retrieving Kaggle credentials from K8s secret
    kaggle_username = open('/mnt/secret/username', 'r').read().strip()
    kaggle_key = open('/mnt/secret/key', 'r').read().strip()

    # kaggle username from the secret
    os.environ['KAGGLE_USERNAME'] = kaggle_username

    # kaggle key from the secret
    os.environ['KAGGLE_KEY'] = kaggle_key


    # create directory to store raw data downloaded from Kaggle
    os.mkdir(parent_dir + download_dir)

    # download kaggle stock data
    os.system('kaggle datasets download -d ' + dataset_name + ' -p ' + parent_dir + download_dir)

    # unzip and delete tar file
    with ZipFile(parent_dir + download_dir + dataset_name.split('/')[1] + '.zip', 'r') as zipObj:
        # Extract all the contents of zip file in different directory
        zipObj.extractall(parent_dir + download_dir)

    # deleting zip file
    os.remove(parent_dir + download_dir + dataset_name.split('/')[1] + '.zip')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset_name', type=str, required=True)
    parser.add_argument('--download_dir', type=str, required=True)
    args = parser.parse_args()
    download_dataset_from_kaggle(
        dataset_name=args.dataset_name,
        download_dir=args.download_dir,
        parent_dir='/mnt/data/'
    )
