import os
import kfp
from kfp import dsl
from kubernetes import client as k8s_client
import json
import argparse


def download_kaggle_dataset(
        kaggle_dataset_name="szrlee/stock-time-series-20050101-to-20171231",
        download_dir="djia_30_stock_data",
        data_pvc_name="djia-kaggle-dataset",
        data_pvc_size="1Gi",
        kaggle_credentials_k8s_secret="muneer-kaggle-credentials"
):
    """

    Args:
        kaggle_dataset_name: Name/uri of Kaggle dataset
        download_dir: Directory where dataset will be stored in persistent volume
        data_pvc_name: Name of persistent volume that needs to be created for storing kaggle dataset (powered by NetApp Trident)
        data_pvc_size: Size of the volume
        kaggle_credentials_k8s_secret: K8s secret name storing encrypted (base64) Kaggle credentials

    Return (dsl.VolumeOp, dsl.ContainerOp): Volume operator created to store data and Container operator for preprocessing

    """
    vop = dsl.VolumeOp(
        name="Volume for Kaggle dataset",
        resource_name=data_pvc_name,
        size=data_pvc_size
    )

    cop = dsl.ContainerOp(
        name='consolidate data',
        image='muneer7589/fintech-dataset-download',
        # Download data from Kaggle and use Kaggle credentials (username and key) from secret
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

    return vop, cop


def download_and_preprocess_data(raw_data_dir='djia_30_stock_data',
                                 processed_data_dir='preproc_djia_30_stock_data',
                                 data_pvc='djia-kaggle-dataset'):
    """ Pre-processing raw stock data using just created PVC.

    Args:
        raw_data_dir: Directory where raw dataset is stored in persistent volume
        processed_data: Directory where pre-processed data will be stored in persistent volume
        data_pvc_name (dsl.VolumeOp): Volume operator referring to location where data is stored

    Returns:
        dsl.ContainerOp object: Kubeflow Pipeline component for pre-processing data

    """
    return dsl.ContainerOp(
        name='preprocess stock data',
        image='muneer7589/fintech-preprocess-data',
        # Preprocess stock data to log timeseries and store as timeseries.cvs
        command=['python3.6', 'preprocess_data.py'],
        arguments=[
            '--raw_data_dir', raw_data_dir,
            '--preprocessed_dir', processed_data_dir
        ],
        pvolumes={
            "/mnt/data": data_pvc.volume
        }
    )


def restore_data_from_snapshot(data_snapshot_name, data_pvc_size, data_pvc_name):
    return dsl.VolumeOp(
        name="restore_data_from_snapshot",
        resource_name=data_pvc_name,
        data_source=data_snapshot_name,
        size=data_pvc_size
    )


def preprocess_data(raw_data_dir='djia_30_stock_data',
                    processed_data_dir='preproc_djia_30_stock_data',
                    data_pvc_name='djia-kaggle-dataset', restored_snapshot=False):
    """ Pre-processing raw stock data using existing volume.

    Args:
        raw_data_dir: Directory where raw dataset is stored in persistent volume
        processed_data: Directory where pre-processed data will be stored in persistent volume
        data_pvc_name: PVC name where data (raw and pre-processed) is stored
        restored_snapshot (bool): True/False.

    Returns:
        dsl.ContainerOp object: Kubeflow Pipeline component for pre-processing data

    """

    if restored_snapshot:
        data_volume = data_pvc_name.volume
    else:
        data_volume = dsl.PipelineVolume(pvc=data_pvc_name)

    return dsl.ContainerOp(
        name='preprocess stock data',
        image='muneer7589/fintech-preprocess-data',
        # Preprocess stock data to log timeseries and store as timeseries.cvs
        command=['python3.6', 'preprocess_data.py'],
        arguments=[
            '--raw_data_dir', raw_data_dir,
            '--preprocessed_dir', processed_data_dir
        ],
        pvolumes={
            "/mnt/data": data_volume
        }
    )


def train_use_existing_model_pvc(model_name='FlatModel',
                                 itr=3000,
                                 input_features=24,
                                 model_tag='v1',
                                 processed_data_dir='preproc_djia_30_stock_data/',
                                 model_path='models/',
                                 model_pvc_name='djia-time-series-model',
                                 download_or_snapshot_data=False,
                                 data_pvc='djia-kaggle-dataset',
                                 data_pvc_name='djia-kaggle-dataset'
                                 ):
    if download_or_snapshot_data:
        data_volume = data_pvc.volume
    else:
        data_volume = dsl.PipelineVolume(pvc=data_pvc_name)

    return dsl.ContainerOp(
        name='training using existing PVC for training model',
        image='muneer7589/fintech-train',
        # Training on pre-processed time series data
        command=['python3.6', 'timeseries_training.py'],
        arguments=[
            '--preprocessed_data_path', processed_data_dir,
            '--tag', model_tag,
            '--model_path', model_path,
            '--model', model_name,
            '--itr', itr,
            '--input_features', input_features,

        ],
        pvolumes={"/mnt/models": dsl.PipelineVolume(pvc=model_pvc_name),
                  "/mnt/data": data_volume},
        file_outputs={'mlpipeline_metrics': '/mlpipeline-metrics.json',
                      'accuracy': '/tmp/accuracy'}
    )


def train_create_model_pvc(model_name='FlatModel',
                           itr=3000,
                           input_features=24,
                           model_tag='v1',
                           processed_data_dir='preproc_djia_30_stock_data/',
                           model_path='models/',
                           model_pvc_name='djia-time-series-model',
                           model_pvc_size='1Gi',
                           download_or_snapshot_data=False,
                           data_pvc='djia-kaggle-dataset',
                           data_pvc_name='djia-kaggle-dataset'
                           ):
    if download_or_snapshot_data:
        data_volume = data_pvc.volume
    else:
        data_volume = dsl.PipelineVolume(pvc=data_pvc_name)

    model_vop = dsl.VolumeOp(
        name="model volume creation",
        resource_name=model_pvc_name,
        size=model_pvc_size
    )

    return dsl.ContainerOp(
        name='training using existing PVC for training model',
        image='muneer7589/fintech-train',
        # Training on pre-processed time series data
        command=['python3.6', 'timeseries_training.py'],
        arguments=[
            '--preprocessed_data_path', processed_data_dir,
            '--tag', model_tag,
            '--model_path', model_path,
            '--model', model_name,
            '--itr', itr,
            '--input_features', input_features,

        ],
        pvolumes={"/mnt/models": model_vop.volume,
                  "/mnt/data": data_volume},
        file_outputs={'mlpipeline_metrics': '/mlpipeline-metrics.json',
                      'accuracy': '/tmp/accuracy'}
    )


@dsl.pipeline(
    name="Stock Time Series Forecast",
    description="Time Series Forecast for stock based on historic data."
)
def stock_time_series(
        download_data="True",
        kaggle_dataset_name="szrlee/stock-time-series-20050101-to-20171231",
        data_pvc_name="djia-kaggle-dataset",
        raw_data_dir="djia_30_stock_data/",
        processed_data_dir="preproc_djia_30_stock_data/",
        data_pvc_size="1Gi",
        restore_data_from_snasphot="False",
        data_snapshot_name="snapshot-djia-kaggle-dataset",
        kaggle_credentials_k8s_secret="muneer-kaggle-credentials",
        itr=3000,
        input_features=24,
        model_name='FlatModel',
        model_tag='v1',
        model_path='models/',
        use_existing_model_pvc="False",
        model_pvc_name="djia-time-series-model",
        model_pvc_size="1Gi"
):
    """:arg"""
    with dsl.Condition(download_data == "True"):
        vop, _download_data = download_kaggle_dataset(
            kaggle_dataset_name=kaggle_dataset_name,
            download_dir=raw_data_dir,
            data_pvc_name=data_pvc_name,
            data_pvc_size=data_pvc_size,
            kaggle_credentials_k8s_secret=kaggle_credentials_k8s_secret
        )

        _download_preprocess_data = download_and_preprocess_data(raw_data_dir=raw_data_dir,
                                                                 processed_data_dir=processed_data_dir,
                                                                 data_pvc=vop).after(_download_data)

        with dsl.Condition(use_existing_model_pvc == "True"):
            train_use_existing_model_pvc(model_name=model_name,
                                         itr=itr,
                                         input_features=input_features,
                                         model_tag=model_tag,
                                         processed_data_dir=processed_data_dir,
                                         model_path=model_path,
                                         model_pvc_name=model_pvc_name,
                                         download_or_snapshot_data=True,
                                         data_pvc=vop).after(_download_preprocess_data),

        with dsl.Condition(use_existing_model_pvc == "False"):
            train_create_model_pvc(model_name=model_name,
                                   itr=itr,
                                   input_features=input_features,
                                   model_tag=model_tag,
                                   processed_data_dir=processed_data_dir,
                                   model_path=model_path,
                                   model_pvc_name=model_pvc_name,
                                   model_pvc_size=model_pvc_size,
                                   data_pvc_name=data_pvc_name,
                                   download_or_snapshot_data=True,
                                   data_pvc=vop).after(_download_preprocess_data)

    with dsl.Condition(download_data == "False"):
        with dsl.Condition(restore_data_from_snasphot == "False"):
            _preprocess_data = preprocess_data(raw_data_dir=raw_data_dir,
                                               processed_data_dir=processed_data_dir,
                                               data_pvc_name=data_pvc_name)

            with dsl.Condition(use_existing_model_pvc == "True"):
                train_use_existing_model_pvc(model_name=model_name,
                                             itr=itr,
                                             input_features=input_features,
                                             model_tag=model_tag,
                                             processed_data_dir=processed_data_dir,
                                             model_path=model_path,
                                             model_pvc_name=model_pvc_name,
                                             download_or_snapshot_data=False,
                                             data_pvc_name=data_pvc_name).after(_preprocess_data),

            with dsl.Condition(use_existing_model_pvc == "False"):
                train_create_model_pvc(model_name=model_name,
                                       itr=itr,
                                       input_features=input_features,
                                       model_tag=model_tag,
                                       processed_data_dir=processed_data_dir,
                                       model_path=model_path,
                                       model_pvc_name=model_pvc_name,
                                       model_pvc_size=model_pvc_size,
                                       download_or_snapshot_data=False,
                                       data_pvc_name=data_pvc_name).after(_preprocess_data)

        with dsl.Condition(restore_data_from_snasphot == "True"):
            vop = restore_data_from_snapshot(data_snapshot_name, data_pvc_size, data_pvc_name)

            _preprocess_data = preprocess_data(raw_data_dir=raw_data_dir,
                                               processed_data_dir=processed_data_dir,
                                               data_pvc_name=vop, restored_snapshot=True)

            with dsl.Condition(use_existing_model_pvc == "True"):
                train_use_existing_model_pvc(model_name=model_name,
                                             itr=itr,
                                             input_features=input_features,
                                             model_tag=model_tag,
                                             processed_data_dir=processed_data_dir,
                                             model_path=model_path,
                                             model_pvc_name=model_pvc_name,
                                             download_or_snapshot_data=True,
                                             data_pvc=vop).after(_preprocess_data),

            with dsl.Condition(use_existing_model_pvc == "False"):
                train_create_model_pvc(model_name=model_name,
                                       itr=itr,
                                       input_features=input_features,
                                       model_tag=model_tag,
                                       processed_data_dir=processed_data_dir,
                                       model_path=model_path,
                                       model_pvc_name=model_pvc_name,
                                       model_pvc_size=model_pvc_size,
                                       download_or_snapshot_data=True,
                                       data_pvc=vop).after(_preprocess_data)


if __name__ == '__main__':

    # Using git_commit id passed by Jenkins at runtime with pipeline name to create unique pipeline version names linked with Jenkins build
    parser = argparse.ArgumentParser()
    parser.add_argument('--git_commit', required=True)
    args = parser.parse_args()

    pipeline_file_name = "fintech_timeseries-prep-train-pipeline.yaml"
    kfp.compiler.Compiler().compile(stock_time_series, pipeline_file_name)

    with open('./config/pipeline.json') as pipeline_config:
        pipeline_config_data = json.load(pipeline_config)
        pipeline_metadata = pipeline_config_data['pipeline_metadata']

    if pipeline_metadata['use_existing_pipeline'] == "True":
        resp = kfp.Client().upload_pipeline_version(pipeline_package_path=pipeline_file_name,
                                             pipeline_id=pipeline_metadata['pipeline_id'],
                                             pipeline_version_name=pipeline_metadata['pipeline_name'] + str(
                                                 args.git_commit))

        # Updating pipeline_version_id pipeline.config
        pipeline_config_data['pipeline_metadata']['pipeline_version_id'] = resp.to_dict()['id']

    else:
        resp = kfp.Client().upload_pipeline(pipeline_package_path=pipeline_file_name,
                                     pipeline_name=pipeline_metadata['pipeline_name'] + str(args.git_commit),
                                     description=pipeline_metadata['description'])

        # Updating pipeline_id in pipeline.config with newly created pipeline id
        pipeline_config_data['pipeline_metadata']['pipeline_id'] = resp.to_dict()['id']

        # Updating pipeline_version_id pipeline.config
        pipeline_config_data['pipeline_metadata']['pipeline_version_id'] = resp.to_dict()['default_version']['id']
        
    # Delete KF pipeline file after upload
    os.remove(pipeline_file_name)

    # Updating config file
    with open('./config/pipeline.json', 'w+') as pipeline_config:
        json.dump(pipeline_config_data, pipeline_config)

    # flag used as a check whether git push is needed or not. Saving it to file so it will be used later by Jenkins
    with open('git_push.txt', 'w') as git_push:
        git_push.write("True")
