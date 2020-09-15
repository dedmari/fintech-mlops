import logging
import json
import os
import argparse
import time
import sys
import pandas as pd
import tensorflow as tf
from tensorflow.python.lib.io import file_io


class FlatModel():
    """Neural network model that contains only single layer."""

    def __init__(self, nr_predictors, nr_classes):
        """
        Args:
          nr_predictors (int): amount of predictors
          nr_classes (int): amount of classes
        """
        self._nr_predictors = nr_predictors
        self._nr_classes = nr_classes

    @property
    def nr_predictors(self):
        """Amount of predictors property."""
        return self._nr_predictors

    @property
    def nr_classes(self):
        """Amount of classes property."""
        return self._nr_classes

    def build_model(self, feature_data):
        """Builds the tensorflow model.
        Args:
          feature_data (tf. tensors): feature tensors
        Returns:
          model: tensorflow graph
        """
        weights = tf.Variable(tf.truncated_normal([self._nr_predictors, self._nr_classes],
                                                  stddev=0.0001))
        biases = tf.Variable(tf.ones([self._nr_classes]))

        model = tf.nn.softmax(tf.matmul(feature_data, weights) + biases)

        return model


class DeepModel():
    """Neural network model that contains two hidden layers."""

    def __init__(self, nr_predictors, nr_classes, dim_hidden1=50, dim_hidden2=25):
        """
        Args:
          nr_predictors (int): amount of predictors
          nr_classes (int): amount of classes
          dim_hidden1 (int): amount of neurons in first hidden layer
          dim_hidden2 (int): amount of neurons in second hidden layer
        """
        self._nr_predictors = nr_predictors
        self._nr_classes = nr_classes
        self.dim_hidden1 = dim_hidden1
        self.dim_hidden2 = dim_hidden2

    @property
    def nr_predictors(self):
        """Amount of predictors property."""
        return self._nr_predictors

    @property
    def nr_classes(self):
        """Amount of classes property."""
        return self._nr_classes

    def build_model(self, feature_data):
        """Builds the tensorflow model.
        Args:
          feature_data (tf. tensors): feature tensors
        Returns:
          model: tensorflow graph
        """
        weights1 = tf.Variable(tf.truncated_normal([self._nr_predictors, self.dim_hidden1],
                                                   stddev=0.0001))
        biases1 = tf.Variable(tf.ones([self.dim_hidden1]))

        weights2 = tf.Variable(tf.truncated_normal([self.dim_hidden1, self.dim_hidden2],
                                                   stddev=0.0001))
        biases2 = tf.Variable(tf.ones([self.dim_hidden2]))

        weights3 = tf.Variable(tf.truncated_normal([self.dim_hidden2, self.nr_classes],
                                                   stddev=0.0001))
        biases3 = tf.Variable(tf.ones([self._nr_classes]))

        hidden_layer_1 = tf.nn.relu(tf.matmul(feature_data, weights1) + biases1)
        hidden_layer_2 = tf.nn.relu(tf.matmul(hidden_layer_1, weights2) + biases2)
        model = tf.nn.softmax(tf.matmul(hidden_layer_2, weights3) + biases3)

        return model


def train_test_split(training_test_data, train_test_ratio=0.8):
    """Splits the data into a training and test set according to the provided ratio.
    Args:
      training_test_data (pandas.dataframe): dict with time series
      train_test_ratio (float): ratio of train test split
    Returns:
      tensors: predictors and classes tensors for training and respectively test set
    """
    predictors_tf = training_test_data[training_test_data.columns[2:]]
    classes_tf = training_test_data[training_test_data.columns[:2]]

    training_set_size = int(len(training_test_data) * train_test_ratio)

    train_test_dict = {'training_predictors_tf': predictors_tf[:training_set_size],
                       'training_classes_tf': classes_tf[:training_set_size],
                       'test_predictors_tf': predictors_tf[training_set_size:],
                       'test_classes_tf': classes_tf[training_set_size:]}

    return train_test_dict


def tf_calc_confusion_matrix_ops(actuals, predictions):
    """Constructs the Tensorflow operations for obtaining the confusion matrix operators.

    Args:
      actuals (tf.tensor): tensor that contain actuals
      predictions (tf.tensor): tensor that contains predictions

    Returns:
      tensors: true_postive, true_negative, false_positive, false_negative

    """

    ones_like_actuals = tf.ones_like(actuals)
    zeros_like_actuals = tf.zeros_like(actuals)
    ones_like_predictions = tf.ones_like(predictions)
    zeros_like_predictions = tf.zeros_like(predictions)

    tp_op = tf.reduce_sum(
        tf.cast(
            tf.logical_and(
                tf.equal(actuals, ones_like_actuals),
                tf.equal(predictions, ones_like_predictions)
            ),
            "float"
        )
    )

    tn_op = tf.reduce_sum(
        tf.cast(
            tf.logical_and(
                tf.equal(actuals, zeros_like_actuals),
                tf.equal(predictions, zeros_like_predictions)
            ),
            "float"
        )
    )

    fp_op = tf.reduce_sum(
        tf.cast(
            tf.logical_and(
                tf.equal(actuals, zeros_like_actuals),
                tf.equal(predictions, ones_like_predictions)
            ),
            "float"
        )
    )

    fn_op = tf.reduce_sum(
        tf.cast(
            tf.logical_and(
                tf.equal(actuals, ones_like_actuals),
                tf.equal(predictions, zeros_like_predictions)
            ),
            "float"
        )
    )

    return tp_op, tn_op, fp_op, fn_op


def tf_calc_confusion_metrics(true_pos, true_neg, false_pos, false_neg):
    """Construct the Tensorflow operations for obtaining the confusion matrix.

    Args:
      true_pos (tf.tensor): tensor with true positives
      true_neg (tf.tensor): tensor with true negatives
      false_pos (tf.tensor): tensor with false positives
      false_neg (tf.tensor): tensor with false negatives

    Returns:
      tensor calculations: precision, recall, f1_score and accuracy

    """
    tpfn = float(true_pos) + float(false_neg)
    tpr = 0 if tpfn == 0 else float(true_pos) / tpfn

    total = float(true_pos) + float(false_pos) + float(false_neg) + float(true_neg)
    accuracy = 0 if total == 0 else (float(true_pos) + float(true_neg)) / total

    recall = tpr
    tpfp = float(true_pos) + float(false_pos)
    precision = 0 if tpfp == 0 else float(true_pos) / tpfp

    f1_score = 0 if recall == 0 else (2 * (precision * recall)) / (precision + recall)

    print('Precision = ', precision)
    print('Recall = ', recall)
    print('F1 Score = ', f1_score)
    print('Accuracy = ', accuracy)

    return {'precision': precision, 'recall': recall, 'f1': f1_score,
            'accuracy': accuracy}


def tf_confusion_matrix(model, actual_classes, session, feed_dict):
    """Calculates confusion matrix when training.

    Args:
      model (object): instance of the model class Object
      actual_classes (tf.tensor): tensor that contains the actual classes
      session (tf.session): tensorflow session in which the tensors are evaluated
      feed_dict (dict): dictionary with features and actual classes


    """

    predictions = tf.argmax(model, 1)
    actuals = tf.argmax(actual_classes, 1)
    tp_op, tn_op, fp_op, fn_op = tf_calc_confusion_matrix_ops(actuals, predictions)
    true_pos, true_neg, false_pos, false_neg = \
        session.run(
            [tp_op, tn_op, fp_op, fn_op],
            feed_dict
        )

    return tf_calc_confusion_metrics(true_pos, true_neg, false_pos, false_neg)


def parse_arguments(argv):
    """Parse command line arguments
    Args:
        argv (list): list of command line arguments including program name
        Returns:
            The parsed arguments as returned by argparse.ArgumentParser
    """
    parser = argparse.ArgumentParser(description='Training')
    parser.add_argument('--model',
                      type=str,
                      help='model to be used for training',
                      default='DeepModel',
                      choices=['FlatModel', 'DeepModel'])
    parser.add_argument('--itr',
                      type=int,
                      help='number of iterations to train',
                      default=5001)
    parser.add_argument('--input_features',
                        type=int,
                        help='input features',
                        default=24)
    parser.add_argument('--tag',
                      type=str,
                      help='tag of the model',
                      default='v1')
    parser.add_argument('--preprocessed_data_path',
                      type=str,
                      help='Path where pre-processed data is stored',
                      default='prep_dataset1/')
    parser.add_argument('--model_path',
                      type=str,
                      help='Path where trained model is stored',
                      default='models/')
    parser.add_argument('--parent_dir_data',
                        type=str,
                        help='Path where data is saved',
                        default='/mnt/data/')
    parser.add_argument('--parent_dir_model',
                        type=str,
                        help='Path where data is saved',
                        default='/mnt/')

    args, _ = parser.parse_known_args(args=argv[1:])

    return args



def run_training(argv=None):
    """Runs the ML model training on processed time-series data.
    Args:
        args: args that are passed when submitting the training
        Returns:
    """

    # parse args
    args = parse_arguments(sys.argv if argv is None else argv)
    logging.info('getting the ML model config to use...')

    if args.model == 'FlatModel':
        model = FlatModel(nr_predictors=args.input_features, nr_classes=2)
    elif args.model == 'DeepModel':
        model = DeepModel(nr_predictors=args.input_features, nr_classes=2)
    else:
        print('Model not available. Available options are FlatModel and DeepModel. Using FlatModel by default.')
        model = FlatModel(nr_predictors=args.input_features, nr_classes=2)

    # get the data
    logging.info('loading pre-processed time-series data...')
    file_path = os.path.join(args.parent_dir_data, args.preprocessed_data_path, 'time_series.csv')
    time_series = pd.read_csv(file_path)
    training_test_data = train_test_split(time_series, 0.8)

    # define training objective
    logging.info('defining the training objective...')
    sess = tf.Session()
    feature_data = tf.placeholder("float", [None, args.input_features])
    actual_classes = tf.placeholder("float", [None, 2])

    model = model.build_model(feature_data)
    cost = -tf.reduce_sum(actual_classes * tf.log(model))
    train_opt = tf.train.AdamOptimizer(learning_rate=0.0001).minimize(cost)
    init = tf.global_variables_initializer()
    sess.run(init)

    # train model
    correct_prediction = tf.equal(tf.argmax(model, 1), tf.argmax(actual_classes, 1))
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))

    logging.info('training the model...')
    time_dct = {}
    time_dct['start'] = time.time()

    for i in range(1, args.itr):
        sess.run(
            train_opt,
            feed_dict={
                feature_data: training_test_data['training_predictors_tf'].values,
                actual_classes: training_test_data['training_classes_tf'].values.reshape(
                    len(training_test_data['training_classes_tf'].values), 2)
            }
        )
        if i % 1000 == 0:
            train_acc = sess.run(
                accuracy,
                feed_dict={
                    feature_data: training_test_data['training_predictors_tf'].values,
                    actual_classes: training_test_data['training_classes_tf'].values.reshape(
                        len(training_test_data['training_classes_tf'].values), 2)
                }
            )
            print(i, train_acc)
    time_dct['end'] = time.time()
    logging.info('training took {0:.2f} sec'.format(time_dct['end'] - time_dct['start']))
    # print results of confusion matrix

    logging.info('validating model on test set...')
    feed_dict = {
        feature_data: training_test_data['test_predictors_tf'].values,
        actual_classes: training_test_data['test_classes_tf'].values.reshape(
            len(training_test_data['test_classes_tf'].values), 2)
    }
    test_acc = tf_confusion_matrix(model, actual_classes, sess,
                                         feed_dict)['accuracy']

    # create signature for TensorFlow Serving
    logging.info('Saving trained model...')

    model_path = os.path.join(args.parent_dir_model, args.model_path, args.tag)

    tf.saved_model.simple_save(
        sess,
        model_path,
        inputs={'predictors': feature_data},
        outputs={'prediction': tf.argmax(model, 1),
                 'model-tag': tf.constant([str(args.tag)])}
    )

    metrics_info = {
        'metrics': [{
            'name': 'accuracy-train',
            'numberValue': float(train_acc),
            'format': "PERCENTAGE"
        }, {
            'name': 'accuracy-test',
            'numberValue': float(test_acc),
            'format': "PERCENTAGE"
        }]}
    with file_io.FileIO('/mlpipeline-metrics.json', 'w') as f:
        json.dump(metrics_info, f)

    with open("/tmp/accuracy", "w") as output_file:
        output_file.write(str(float(test_acc)))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run_training()
