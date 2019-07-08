#
###############################################################################
#                                                                             #
#							 Copyright (c)									  #
#                         All rights reserved.                                #
#                                                                             #
###############################################################################
#
#  Filename:     intensive_snn_tests.py
#
###############################################################################
#  Description:
#
#  (For a detailed description look at the object description in the UML model)
#
###############################################################################
# History
################################################################################
# File:		   intensive_snn_tests.py
# Version:     8.0
# Author/Date: Junseok Oh / 2019-05-23
# Change:      snLength: 4096
#              epoch: 20, 1+19
#              # of test cases: 30
#              Conv(4, 4x4, Non-bias, L1=0.0007), activation function(tanh(x)), 
#              maxPooling(2x2), Dense(10), activation function(softmax)
#              Stochastic Conv(Mux+STanh, Adaptive), Stochastic Dense(Normal+none)
# Cause:       Need short description for this file
# Initiator:   Junseok Oh
###############################################################################
import keras
from keras.datasets import mnist
from keras.models import Sequential, Model
from keras.layers import Dense, Dropout, Flatten, Activation
from keras.layers import Conv2D, MaxPooling2D
from keras import backend as K
from keras import regularizers
from keras.callbacks import Callback
import WeightScaling_intensiveTests_55
from keras.utils.generic_utils import get_custom_objects
import numpy as np
import random
from snn.holayer import HOModel, HOMaxPoolingExact, HOMaxPoolingAprox, HOConvolution, HOConnected
from snn.utils import HOUtils
from snn.bnlayer import BNModel
import global_variables
from plotly import tools
import plotly as py
import plotly.graph_objs as go
import copy

# misc functions
def first_layer_activation(x):
    return K.tanh(x)
    #return K.relu(x)/10
    #return K.tanh(x/2.5)


def createSN(x, length):
    """create bipolar SN by comparing random vector elementwise to SN value x"""
    # rand = np.random.rand(length)*2.0 - 1.0
    # x_SN = np.less(rand, x)
    large = np.random.rand(1)
    x_SN = np.full(length, False)
    if large:
        for i in range(int(np.ceil(((x+1)/2)*length))):
            x_SN[i] = True
    else:
        for i in range(int(np.floor(((x+1)/2)*length))):
            x_SN[i] = True
    np.random.shuffle(x_SN)
    return x_SN

def stochtoint(x):
    """convert bipolar stochastic number to integer"""
    return (sum(x)/len(x))*2.0 - 1.0


#get_custom_objects().update({'first_layer_activation': Activation(first_layer_activation)})

np.set_printoptions(threshold=np.inf)

batch_size = 128
num_classes = 10
epochs = 20
cntEpochs = 0

# Define the global variables
global_variables.DefineGlobalVariables()

# input image dimensions
img_rows, img_cols = 28, 28

# the data, shuffled and split between train and test sets
(x_train, y_train), (x_test, y_test) = mnist.load_data()

x_train = x_train.astype('float32')
x_test = x_test.astype('float32')
x_train /= 255
x_test /= 255
x_train = x_train[:60000]
x_test = x_test[:800]

print('x_train shape:', x_train.shape)
print(x_train.shape[0], 'train samples')
print(x_test.shape[0], 'test samples')

# convert class vectors to binary class matrices
y_train = keras.utils.to_categorical(y_train, num_classes)
y_test = keras.utils.to_categorical(y_test, num_classes)
y_train = y_train[:60000]
y_test = y_test[:800]
print(y_train.shape)

if K.image_data_format() == 'channels_first':
    x_train = x_train.reshape(x_train.shape[0], 1, img_rows, img_cols)
    x_test = x_test.reshape(x_test.shape[0], 1, img_rows, img_cols)
    input_shape = (1, img_rows, img_cols)
else:
    x_train = x_train.reshape(x_train.shape[0], img_rows, img_cols, 1)
    x_test = x_test.reshape(x_test.shape[0], img_rows, img_cols, 1)
    input_shape = (img_rows, img_cols, 1)

# 1st Model
global_variables.bnModel = BNModel(6)
global_variables.bnModel.SetId(1) # Set as the 1st model
global_variables.bnModel[0] = Conv2D(4, kernel_size=(4, 4),
                                     input_shape=input_shape,
                                     use_bias=False,
                                     kernel_regularizer=regularizers.l1(0.0007))
global_variables.bnModel[1] = Activation(first_layer_activation)
global_variables.bnModel[2] = MaxPooling2D(pool_size=(2, 2))
global_variables.bnModel[3] = Flatten()
global_variables.bnModel[4] = Dense(num_classes)
global_variables.bnModel[5] = Activation('softmax')
global_variables.bnModel.LoadLayers()
global_variables.bnModel.Compile(loss=keras.losses.mse,
                                 optimizer=keras.optimizers.Adadelta(),
                                 metrics=['accuracy'])
lobal_variables.bnModel.Fit(x_train, y_train,
                             batch_size=batch_size,
                             epochs=epochs,
                             verbose=0,
                             callbacks=[WeightScaling_intensiveTests_55.WeightScale()],
                             validation_data=(x_test, y_test))
global_variables.bnModel.Load_weights('results/#Epoch20 weights of 1st model_tests55.h5')
global_variables.bnModel.Evaluate(x_test[:500], y_test[:500], verbose=0, indexModel=1)
global_variables.bnModel.Evaluate(x_test[:107], y_test[:107], verbose=0, indexModel=1)

# Optimize the neural network
global_variables.bnModel.OptimizeNetwork('tests55',
                                         'results/#Epoch20 weights of 1st model_tests55.h5',
                                         'results/#Epoch1 weights of 1st model_tests55.h5',
                                         WeightScaling_intensiveTests_55,
                                         x_train=x_train,
                                         y_train=y_train,
                                         x_test=x_test,
                                         y_test=y_test,
                                         epochs=epochs-1,
                                         batch_size=batch_size
                                         )

# Get the layer models from bnModel
layer1model = global_variables.bnModel[0]
layer2model = global_variables.bnModel[1]
layer3model = global_variables.bnModel[2]
layer4model = global_variables.bnModel[3]
layer5model = global_variables.bnModel[4]
layer6model = global_variables.bnModel[5]

# Hybrid NN with stochastic convolutional layer and binary dense layer

# SN length
length = 1024*4

# Make instance of util and bnModel
ut = HOUtils()
model2 = global_variables.bnModel.GetModel()
global_variables.bnModel = 0

# weights and biases of the convolutional layer
#bias_SNs = ut.GetConvolutionLayerBiasesSN(model, 1, length)
#weight_SNs, listIndex = ut.GetConvolutionLayerWeightsSN(model2, 1, length)
weight_SNs, bias_SNs, listIndex = ut.GetConvolutionLayerWeightsBiasesSN(model2, 1, length, Adaptive="True")

# weights and biases of dense layer
dense_biases = ut.GetConnectedLayerBiases(model2, 5)
dense_weight_SNs = ut.GetConnectedLayerWeightsSN(model2, 5, length)

output = np.zeros((1, 10))
correct_predictions = 0
test_index = 0
output_mse = 0

print('start stochastic NN')
# for each input in the test set
for r in range(30):
    x = x_test[test_index]
    print(test_index)

    # build input SN matrix
    SN_input_matrix = np.full((img_rows, img_cols, length), False)
    for i in range(img_rows):
        for j in range(img_cols):
            SN_input_matrix[i, j] = createSN(x[0, i, j], length)
    del(x)
    print('inputs generated')

    # Generate the HOModel
    hoModel = HOModel(SN_input_matrix)
    del(SN_input_matrix)

    # convolutional layer
    hoModel.SetNumOutputPlanes(4) # The number of slices:4
    hoModel.SetWeights(weight_SNs)
    hoModel.SetZeroBias(4)
    hoModel.SetListIndex(listIndex)
    #hoModel.SetBias(bias_SNs)
    hoConvLayer = HOConvolution(4, 4, length, baseMode="Mux", activationFunc="STanh")
    hoModel.Activation(hoConvLayer, stride=1)
    del(hoConvLayer)
    print("conv layer done")

    if(test_index % 10 == 0):
        ut.SaveInTxtFormat('v8.0_intensive_snn_tests55_conv', test_index,
                           hoModel.GetOutputMatrix(), 4, 25, 25,
                           layer2model, x_test)
        print(str(test_index+1)+' conv layer results saved in txt format')

    # max pooling layer
    hoMaxLayer = HOMaxPoolingExact(2, 2, length)
    hoModel.Activation(hoMaxLayer, stride=2) # Stride:2, filterSize:2x2
    del(hoMaxLayer)
    print("maxpool layer done")
    if(test_index % 10 == 0):
        ut.SaveInTxtFormat('v8.0_intensive_snn_tests55_maxpool', test_index,
                           hoModel.GetOutputMatrix(), 4, 12, 12,
                           layer3model, x_test)
        print(str(test_index+1)+' maxpool layer results saved in txt format')

    # First dense layer
    hoModel.SetDenseWeights(dense_weight_SNs)
    hoModel.SetDenseBias(dense_biases)
    hoDenseLayer = HOConnected(length, stochToInt="Normal", activationFunc="None")
    hoModel.Activation(hoDenseLayer, num_classes=num_classes)
    del(hoDenseLayer)
    ################### For debugging purpose, save the intermidiate results in the local variable ###################
    dense_output = hoModel.GetOutputMatrix()
    print("dense 1 output from Binary NN")
    BNN_prediction = layer5model.predict(np.asarray([x_test[test_index]]))
    print(BNN_prediction)
    del(BNN_prediction)
    print("dense 1 output from Stochastic NN")
    print(dense_output)
    ################################################################################################################
    print('dense 1 layer done')

    out_error = 0
    out = layer5model.predict(np.asarray([x_test[test_index]]))
    for i in range(10):
        out_error = out_error + (dense_output[0, i] - out[0, i])**2

    print("out_error:", out_error)
    output_mse = output_mse + out_error

    # softmax activation
    dense_out_exp = [np.exp(i) for i in dense_output]
    exp_sum_out = np.sum(dense_out_exp)
    hybrid_output = [i/exp_sum_out for i in dense_out_exp]

    if(np.argmax(hybrid_output) == np.argmax(y_test[test_index])):
        correct_predictions = correct_predictions + 1
    test_index = test_index + 1

    current_accuracy = correct_predictions/test_index

    print(current_accuracy)

    del(dense_output)
    del(hoModel)

correct_predictions = correct_predictions/30
print("correct classifications:", correct_predictions)
output_mse = output_mse/30
print("output_mse:", output_mse)