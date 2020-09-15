import numpy as np
import pandas as pd
import glob
import os
import argparse
import logging


def data_to_time_series(
        tickers,
        raw_data_path='datset1/',
        preprocess_data_path='prep_dataset1/',
        parent_dir='/mnt/data/'
):
    """ Preprocesses raw data into time series.

    Args:
        tickers (list): list of tickers to load data for e.g. GOOGL
        raw_data_path (str): Path of raw data
        preprocess_data_path (str): Path of preprocessed data
        parent_dir (str): Parent directory or mount path

    Returns:
        pandas.dataframe: time series dataframe

    """
    # reading raw CSV files (only Date and Close) and only selecting files defined in tickers
    all_stocks = {}
    for raw_file in glob.glob(parent_dir + raw_data_path + '*.csv'):
        stock_name = raw_file.split('/')[-1].split('_')[0]
        if stock_name in tickers:
            all_stocks[stock_name] = pd.read_csv(raw_file).set_index('Date')

    if not all_stocks:
        logging.info('No data available..')
    else:
        logging.info('starting data preprocessing...')
        # sort and fill missing values
        stocks_close_data = pd.DataFrame()
        for ticker in tickers:
            stocks_close_data['{}_close'.format(ticker)] = all_stocks[ticker]['Close']
        stocks_close_data.sort_index(inplace=True)
        stocks_close_data = stocks_close_data.fillna(method='ffill')

        # transform into time series (log)
        log_return_data = pd.DataFrame()

        for ticker in tickers:
            log_return_data['{}_log_return'.format(ticker)] = np.log(
                stocks_close_data['{}_close'.format(ticker)] /
                stocks_close_data['{}_close'.format(ticker)].shift())

        log_return_data['AABA_log_return_positive'] = 0
        log_return_data.loc[log_return_data['AABA_log_return'] >= 0, 'AABA_log_return_positive'] = 1
        log_return_data['AABA_log_return_negative'] = 0
        log_return_data.loc[log_return_data['AABA_log_return'] < 0, 'AABA_log_return_negative'] = 1

        # create dataframe
        training_test_data = pd.DataFrame(
            columns=[
                'AABA_log_return_positive', 'AABA_log_return_negative',
                'AABA_log_return_1', 'AABA_log_return_2', 'AABA_log_return_3',
                'AMZN_log_return_1', 'AMZN_log_return_2', 'AMZN_log_return_3',
                'CSCO_log_return_1', 'CSCO_log_return_2', 'CSCO_log_return_3',
                'GOOGL_log_return_0', 'GOOGL_log_return_1', 'GOOGL_log_return_2',
                'AAPL_log_return_0', 'AAPL_log_return_1', 'AAPL_log_return_2',
                'AXP_log_return_0', 'AXP_log_return_1', 'AXP_log_return_2',
                'BA_log_return_0', 'BA_log_return_1', 'BA_log_return_2',
                'CAT_log_return_0', 'CAT_log_return_1', 'CAT_log_return_2'])

        # fill dataframe with time series
        for i in range(7, len(log_return_data)):
            training_test_data = training_test_data.append(
                {'AABA_log_return_positive': log_return_data['AABA_log_return_positive'].iloc[i],
                 'AABA_log_return_negative': log_return_data['AABA_log_return_negative'].iloc[i],
                 'AABA_log_return_1': log_return_data['AABA_log_return'].iloc[i - 1],
                 'AABA_log_return_2': log_return_data['AABA_log_return'].iloc[i - 2],
                 'AABA_log_return_3': log_return_data['AABA_log_return'].iloc[i - 3],
                 'AMZN_log_return_1': log_return_data['AMZN_log_return'].iloc[i - 1],
                 'AMZN_log_return_2': log_return_data['AMZN_log_return'].iloc[i - 2],
                 'AMZN_log_return_3': log_return_data['AMZN_log_return'].iloc[i - 3],
                 'CSCO_log_return_1': log_return_data['CSCO_log_return'].iloc[i - 1],
                 'CSCO_log_return_2': log_return_data['CSCO_log_return'].iloc[i - 2],
                 'CSCO_log_return_3': log_return_data['CSCO_log_return'].iloc[i - 3],
                 'GOOGL_log_return_0': log_return_data['GOOGL_log_return'].iloc[i],
                 'GOOGL_log_return_1': log_return_data['GOOGL_log_return'].iloc[i - 1],
                 'GOOGL_log_return_2': log_return_data['GOOGL_log_return'].iloc[i - 2],
                 'AAPL_log_return_0': log_return_data['AAPL_log_return'].iloc[i],
                 'AAPL_log_return_1': log_return_data['AAPL_log_return'].iloc[i - 1],
                 'AAPL_log_return_2': log_return_data['AAPL_log_return'].iloc[i - 2],
                 'AXP_log_return_0': log_return_data['AXP_log_return'].iloc[i],
                 'AXP_log_return_1': log_return_data['AXP_log_return'].iloc[i - 1],
                 'AXP_log_return_2': log_return_data['AXP_log_return'].iloc[i - 2],
                 'BA_log_return_0': log_return_data['BA_log_return'].iloc[i],
                 'BA_log_return_1': log_return_data['BA_log_return'].iloc[i - 1],
                 'BA_log_return_2': log_return_data['BA_log_return'].iloc[i - 2],
                 'CAT_log_return_0': log_return_data['CAT_log_return'].iloc[i],
                 'CAT_log_return_1': log_return_data['CAT_log_return'].iloc[i - 1],
                 'CAT_log_return_2': log_return_data['CAT_log_return'].iloc[i - 2]},
                ignore_index=True)

        logging.info("Processed data shape: {}".format(training_test_data.shape))

        if not os.path.exists(parent_dir + preprocess_data_path):
            os.makedirs(parent_dir + preprocess_data_path)

        training_test_data.to_csv(parent_dir + preprocess_data_path + 'time_series.csv', index=False)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument('--raw_data_dir', type=str, required=True)
    parser.add_argument('--preprocessed_dir', type=str, required=True)
    args = parser.parse_args()
    data_to_time_series(tickers=['AABA', 'AMZN', 'CSCO', 'GOOGL', 'AAPL', 'AXP', 'BA', 'CAT'],
                        raw_data_path=args.raw_data_dir,
                        preprocess_data_path=args.preprocessed_dir,
                        parent_dir='/mnt/data/')


