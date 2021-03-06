from tensorflow.python.framework import ops
import tensorflow as tf
from app.cnn_utils import random_mini_batches
from config.APP import model_path
import numpy as np
import logging
logger = logging.getLogger(__name__)

def model1(X_train, Y_train, X_test, Y_test, session, model_name,
           learning_rate=0.003,
           num_epochs=200, minibatch_size=128, lambd=None, print_cost=True):
    """
    Implements a three-layer ConvNet in Tensorflow:
    CONV2D -> RELU -> MAXPOOL -> CONV2D -> RELU -> MAXPOOL -> FLATTEN -> FULLYCONNECTED

    Arguments:
    X_train -- training set, of shape (None, 64, 64, 3)
    Y_train -- test set, of shape (None, n_y = 6)
    X_test -- training set, of shape (None, 64, 64, 3)
    Y_test -- test set, of shape (None, n_y = 6)
    learning_rate -- learning rate of the optimization
    num_epochs -- number of epochs of the optimization loop
    minibatch_size -- size of a minibatch
    print_cost -- True to print the cost every 100 epochs

    Returns:
    train_accuracy -- real number, accuracy on the train set (X_train)
    test_accuracy -- real number, testing accuracy on the test set (X_test)
    parameters -- parameters learnt by the model. They can then be used to predict.
    """

    seed = 1100  # to keep results consistent (numpy seed)
    # (m, n_H0, n_W0, n_C0) = X_train.shape
    # n_y = Y_train.shape[1]
    costs = []  # To keep track of the cost


    m = X_train.shape[0]
    # Create Placeholders of the correct shape
    graph = tf.get_default_graph()
    X = graph.get_tensor_by_name("X:0")
    Y = graph.get_tensor_by_name("Y:0")
    # Initialize parameters
    W1 = graph.get_tensor_by_name("W1:0")
    W2 = graph.get_tensor_by_name("W2:0")
    parameters = {"W1": W1,
                  "W2": W2}

    # Cost function: Add cost function to tensorflow graph
    # cost = graph.get_tensor_by_name("cost:0")
    # if lambd is not None:
    #     cost = compute_cost_reg(cost, parameters, lambd=lambd)

    # Backpropagation: Define the tensorflow optimizer. Use an AdamOptimizer that minimizes the cost.

    # optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(cost)

    # create a saver
    saver = tf.train.Saver()

    # Start the session to compute the tensorflow graph
    # with tf.Session() as sess:

    # Do the training loop
    for epoch in range(num_epochs):

        minibatch_cost = 0.
        num_minibatches = int(m / minibatch_size)  # number of minibatches of size minibatch_size in the train set
        seed = seed + 1
        minibatches = random_mini_batches(X_train, Y_train, minibatch_size, seed)

        for minibatch in minibatches:
            # Select a minibatch
            (minibatch_X, minibatch_Y) = minibatch
            # IMPORTANT: The line that runs the graph on a minibatch.
            # Run the session to execute the optimizer and the cost, the feedict should contain a minibatch for (X,Y).
            ### START CODE HERE ### (1 line)
            _, temp_cost = session.run(graph.get_collection("opt"), feed_dict={X: minibatch_X, Y: minibatch_Y})
            ### END CODE HERE ###

            minibatch_cost += temp_cost / num_minibatches

        # Print the cost every epoch
        if print_cost == True and epoch % 5 == 0:
            print("Cost after epoch %i: %f" % (epoch, minibatch_cost))
        if print_cost == True and epoch % 1 == 0:
            costs.append(minibatch_cost)

    # Calculate the correct predictions
    predict_op = graph.get_tensor_by_name("predict_op:0")
    saver.save(session, model_path + model_name)

    correct_prediction = tf.equal(predict_op, tf.argmax(Y, 1))

    # Calculate accuracy on the test set
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))
    # print(accuracy)
    train_accuracy = accuracy.eval({X: X_train, Y: Y_train})
    test_accuracy = accuracy.eval({X: X_test, Y: Y_test})
    # print("Train Accuracy:", train_accuracy)
    # print("Test Accuracy:", test_accuracy)

    return train_accuracy, test_accuracy, parameters, costs


def splitDataToTrainAndTest(x, y):
    m = x.shape[0]  # number of training examples
    # Step 1: Shuffle (X, Y)
    permutation = list(np.random.permutation(m))
    shuffled_x = x[permutation, :, :, :]
    shuffled_y = y[:, permutation]

    m_train = int(m * 0.9)
    x_train = shuffled_x[0: m_train, :, :, :]
    y_train = shuffled_y[:, 0: m_train]
    x_test = shuffled_x[m_train: m, :, :, :]
    y_test = shuffled_y[:, m_train: m]
    # print(permutation[0:100])
    return x_train, y_train, x_test, y_test


def model(X_train, Y_train, X_test, Y_test, starter_learning_rate=0.003,learning_rate_decay=1,dropout_rate=0,
          num_epochs=200, minibatch_size=128, lambd_train=0, print_cost=True):
    """
    Implements a three-layer ConvNet in Tensorflow:
    CONV2D -> RELU -> MAXPOOL -> CONV2D -> RELU -> MAXPOOL -> FLATTEN -> FULLYCONNECTED

    Arguments:
    X_train -- training set, of shape (None, 64, 64, 3)
    Y_train -- test set, of shape (None, n_y = 6)
    X_test -- training set, of shape (None, 64, 64, 3)
    Y_test -- test set, of shape (None, n_y = 6)
    learning_rate -- learning rate of the optimization
    num_epochs -- number of epochs of the optimization loop
    minibatch_size -- size of a minibatch
    print_cost -- True to print the cost every 100 epochs

    Returns:
    train_accuracy -- real number, accuracy on the train set (X_train)
    test_accuracy -- real number, testing accuracy on the test set (X_test)
    parameters -- parameters learnt by the model. They can then be used to predict.
    """

    ops.reset_default_graph()  # to be able to rerun the model without overwriting tf variables
    tf.set_random_seed(1)  # to keep results consistent (tensorflow seed)
    seed = 3  # to keep results consistent (numpy seed)
    (m, n_H0, n_W0, n_C0) = X_train.shape
    n_y = Y_train.shape[1]
    costs = []  # To keep track of the cost

    # Create Placeholders of the correct shape
    ### START CODE HERE ### (1 line)
    X, Y, lambd, dropout, training = create_placeholders(n_H0, n_W0, n_C0, n_y)
    ### END CODE HERE ###

    # Initialize parameters
    ### START CODE HERE ### (1 line)
    parameters = initialize_parameters()
    ### END CODE HERE ###

    # Forward propagation: Build the forward propagation in the tensorflow graph
    ### START CODE HERE ### (1 line)
    Z3 = forward_propagation(X, parameters, lambd, dropout, training)
    ### END CODE HERE ###

    # Cost function: Add cost function to tensorflow graph
    ### START CODE HERE ### (1 line)
    cost = compute_cost(Z3, Y)
    ### END CODE HERE ###

    # Backpropagation: Define the tensorflow optimizer. Use an AdamOptimizer that minimizes the cost.
    ### START CODE HERE ### (1 line)
    global_step = tf.Variable(0, trainable=False)
    learning_rate = tf.train.exponential_decay(starter_learning_rate, global_step,
                                               100000, learning_rate_decay, staircase=True)
    optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(cost, global_step=global_step)
    tf.add_to_collection("opt", optimizer)
    tf.add_to_collection("opt", cost)
    tf.add_to_collection("opt", global_step)
    ### END CODE HERE ###

    # Initialize all the variables globally
    init = tf.global_variables_initializer()

    # create a saver
    saver = tf.train.Saver()

    # Start the session to compute the tensorflow graph
    with tf.Session() as sess:

        # Run the initialization
        sess.run(init)
        step = 0
        # Do the training loop
        for epoch in range(num_epochs):

            minibatch_cost = 0.
            num_minibatches = int(m / minibatch_size)  # number of minibatches of size minibatch_size in the train set
            seed = seed + 1
            minibatches = random_mini_batches(X_train, Y_train, minibatch_size, seed)

            for minibatch in minibatches:
                # Select a minibatch
                (minibatch_X, minibatch_Y) = minibatch
                # IMPORTANT: The line that runs the graph on a minibatch.
                # Run the session to execute the optimizer and the cost, the feedict should contain a minibatch for (X,Y).
                ### START CODE HERE ### (1 line)
                _, temp_cost, step = sess.run(tf.get_collection("opt"),
                                              feed_dict={X: minibatch_X, Y: minibatch_Y,
                                                         lambd: lambd_train, training: True})#, dropout: dropout_rate
                ### END CODE HERE ###

                minibatch_cost += temp_cost / num_minibatches

            # Print the cost every epoch
            if print_cost == True and epoch % 5 == 0:
                logger.info("LR:%f,Cost after epoch %i(step:%i)\t: %f" % (learning_rate.eval(), epoch, step, minibatch_cost))
            if print_cost == True and epoch % 1 == 0:
                costs.append(minibatch_cost)


        # Calculate the correct predictions
        predict_op = tf.argmax(Z3, 1, name='predict_op')
        saver.save(sess, model_path + "finger-model")
        correct_prediction = tf.equal(predict_op, tf.argmax(Y, 1))

        # Calculate accuracy on the test set
        accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))
        # print(accuracy)
        train_accuracy = accuracy.eval({X: X_train, Y: Y_train, lambd: 0, training: False})#, dropout: 0
        test_accuracy = accuracy.eval({X: X_test, Y: Y_test, lambd: 0, training: False})#, dropout: 0
        # print("Train Accuracy:", train_accuracy)
        # print("Test Accuracy:", test_accuracy)

        return train_accuracy, test_accuracy, parameters, costs


def normalize(X_train_orig, X_test_orig):
    X_train = X_train_orig / 255
    X_test = X_test_orig / 255
    return X_train, X_test


def normalize1(x):
    x = x / 255
    return x


def create_placeholders(n_H0, n_W0, n_C0, n_y):
    """
    Creates the placeholders for the tensorflow session.

    Arguments:
    n_H0 -- scalar, height of an input image
    n_W0 -- scalar, width of an input image
    n_C0 -- scalar, number of channels of the input
    n_y -- scalar, number of classes

    Returns:
    X -- placeholder for the data input, of shape [None, n_H0, n_W0, n_C0] and dtype "float"
    Y -- placeholder for the input labels, of shape [None, n_y] and dtype "float"
    """
    X = tf.placeholder(name='X', shape=(None, n_H0, n_W0, n_C0), dtype=tf.float32)
    Y = tf.placeholder(name='Y', shape=(None, n_y), dtype=tf.float32)
    lambd = tf.placeholder(name='lambd', dtype=tf.float32)
    dropout = tf.placeholder(name='dropout', dtype=tf.float32)
    training = tf.placeholder(name='training', dtype=tf.bool)
    return X, Y, lambd, dropout, training


def initialize_parameters():
    """
    Initializes weight parameters to build a neural network with tensorflow. The shapes are:
                        W1 : [4, 4, 3, 8]
                        W2 : [2, 2, 8, 16]
    Returns:
    parameters -- a dictionary of tensors containing W1, W2
    """

    tf.set_random_seed(1)  # so that your "random" numbers match ours

    W1 = tf.get_variable(name='W1', dtype=tf.float32, shape=(4, 4, 3, 16),
                         initializer=tf.contrib.layers.xavier_initializer(seed=0))
    bias1 = tf.get_variable('bias1', 16, initializer=tf.constant_initializer(0.0))
    W2 = tf.get_variable(name='W2', dtype=tf.float32, shape=(2, 2, 16, 32),
                         initializer=tf.contrib.layers.xavier_initializer(seed=0))
    bias2 = tf.get_variable('bias2', 32, initializer=tf.constant_initializer(0.0))
    parameters = {"W1": W1,
                  "W2": W2,
                  "bias1": bias1,
                  "bias2": bias2}

    return parameters


def forward_propagation(X, parameters, lambd_ph, dropout, training):
    """
    Implements the forward propagation for the model:
    CONV2D -> RELU -> MAXPOOL -> CONV2D -> RELU -> MAXPOOL -> FLATTEN -> FULLYCONNECTED

    Arguments:
    X -- input dataset placeholder, of shape (input size, number of examples)
    parameters -- python dictionary containing your parameters "W1", "W2"
                  the shapes are given in initialize_parameters

    Returns:
    Z3 -- the output of the last LINEAR unit
    """

    # Retrieve the parameters from the dictionary "parameters"
    W1 = parameters['W1']
    W2 = parameters['W2']
    bias1 = parameters['bias1']
    bias2 = parameters['bias2']
    ### START CODE HERE ###
    # layer1
    # CONV2D: stride of 1, padding 'SAME'
    Z1 = tf.nn.conv2d(input=X, filter=W1, strides=(1, 1, 1, 1), padding='SAME')
    # RELU
    A1 = tf.nn.relu(tf.nn.bias_add(Z1, bias1))
    # MAXPOOL: window 8x8, sride 8, padding 'SAME'
    P1 = tf.nn.max_pool(value=A1, ksize=(1, 4, 4, 1), strides=(1, 4, 4, 1), padding='SAME')

    # layer2
    # CONV2D: filters W2, stride 1, padding 'SAME'
    Z2 = tf.nn.conv2d(input=P1, filter=W2, strides=(1, 1, 1, 1), padding='SAME')
    # RELU
    A2 = tf.nn.relu(tf.nn.bias_add(Z2, bias2))
    # MAXPOOL: window 4x4, stride 4, padding 'SAME'
    P2 = tf.nn.max_pool(value=A2, ksize=(1, 4, 4, 1), strides=(1, 4, 4, 1), padding='SAME')

    #layer3
    # FLATTEN
    P2 = tf.layers.flatten(inputs=P2)
    # print(P2)
    # P2_dropout = tf.nn.dropout(P2, rate=dropout)
    # FULLY-CONNECTED without non-linear activation function (not not call softmax).
    # 6 neurons in output layer. Hint: one of the arguments should be "activation_fn=None"
    # Z3 = tf.contrib.layers.fully_connected(P2_dropout, 6, activation_fn=None,
    #                                        weights_regularizer=tf.contrib.layers.l2_regularizer(lambd_ph))

    A21 = tf.layers.dense(P2, 12, activation=tf.nn.relu)
    Z3 = tf.layers.dense(A21, 6, activation=None)
    ### END CODE HERE ###

    return Z3


def compute_cost(Z3, Y):
    """
    Computes the cost

    Arguments:
    Z3 -- output of forward propagation (output of the last LINEAR unit), of shape (6, number of examples)
    Y -- "true" labels vector placeholder, same shape as Z3

    Returns:
    cost - Tensor of the cost function
    """

    ### START CODE HERE ### (1 line of code)
    cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=Z3, labels=Y), name='cost')
    ### END CODE HERE ###

    return cost
