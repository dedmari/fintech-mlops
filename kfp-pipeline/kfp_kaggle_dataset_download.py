import kfp
from kfp import dsl
from kubernetes import client as k8s_client

@dsl.pipeline(
    name="Kaggel dataset download",
    description="Downloading Kaggle dataset and using secrets for retrieving Kaggle credentials."
)
def download_kaggle_dataset(
        kaggle_dataset_name = "szrlee/stock-time-series-20050101-to-20171231",
        download_dir = "djia_30_stock_data",
        data_pvc_name = "djia-kaggle-dataset",
        data_pvc_size = "1Gi",
        kaggle_credentials_k8s_secret = "muneer-kaggle-credentials"
):
    """

    Args:
        kaggle_dataset_name: Name/uri of Kaggle dataset
        download_dir: Directory where dataset will be stored in persistent volume
        data_pvc_name: Name of persistent volume that needs to be created for storing kaggle dataset (powered by NetApp Trident)
        data_pvc_size: Size of the volume
        kaggle_credentials_k8s_secret: K8s secret name storing encrypted (base64) Kaggle credentials

    """
    vop = dsl.VolumeOp(
        name="Volume for Kaggle dataset",
        resource_name=data_pvc_name,
        size=data_pvc_size
    )

    dsl.ContainerOp(
        name='consolidate data',
        image='muneer7589/kaggle-dataset-download',  # Download data from Kaggle and use Kaggle credentials (username and key) from secret
        command=['python3.6', 'download_kaggle_dataset.py'],
        arguments=[
            '--dataset_name', kaggle_dataset_name,
            '--download_dir', download_dir
        ],
        pvolumes={"/mnt/data": vop.volume}
    ).add_pvolumes({
            '/mnt/secret': k8s_client.V1Volume(
                name='kaggle-credentials',
                secret=k8s_client.V1SecretVolumeSource(
                    secret_name=kaggle_credentials_k8s_secret
                )
            )
        }

    )

if __name__ == '__main__':
    kfp.compiler.Compiler().compile(download_kaggle_dataset, "download_kaggle_dataset-pipeline.yaml")