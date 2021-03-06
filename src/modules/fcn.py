# -*- coding: utf-8 -*-

import tensorflow as tf

def multi_denses(
    inputs, out_size, num_layers, func_activation=None,
    weight_decay=0.0, is_train=False, dropout_p=1.0, 
    scope="multi_denses"):
    with tf.variable_scope(scope):
        units = inputs.get_shape().as_list()[-1]
        activation = None #default no activation function
        if func_activation == "relu":
            activation = tf.nn.relu
        elif func_activation == "tanh":
            activation = tf.nn.tanh
        elif func_activation == "sigmoid":
            activation = tf.nn.sigmoid
        else:
            raise NotImplementedError
        
        for i in range(num_layers):
            if i == num_layers-1:
                units = out_size
                activation = None # the final activation is None
            # inputs = tf.cond(tf.equal(is_train, True), lambda: tf.nn.dropout(inputs, dropout_p), lambda: inputs)
            inputs = tf.layers.dense(
                inputs, units, activation, use_bias=True, 
                bias_initializer=tf.glorot_normal_initializer(),
                kernel_initializer=tf.glorot_normal_initializer(),
                bias_regularizer=lambda x: weight_decay*tf.nn.l2_loss(x),
                kernel_regularizer=lambda x: weight_decay*tf.nn.l2_loss(x))

        return inputs

import numpy as np

if __name__ == "__main__":
    inputs = np.random.rand(2,3,4)*10
    print(inputs)
    inputs = tf.constant(inputs)

    # outputs = multi_denses(inputs, out_size=4, num_layers=1)
    outputs = tf.layers.dense(
        inputs, units=4, activation=tf.nn.tanh, use_bias=True)

    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())

        out = sess.run(outputs)
        print(out)