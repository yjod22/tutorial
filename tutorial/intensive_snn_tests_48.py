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
# Version:     6.4
# Author/Date: Junseok Oh / 2019-03-24
# Change:      snLength: 4096
#              epoch: 2, 20
#              # of test cases: 100
#              Conv(4, 4x4, non-bias, L1-0.0007), activation function(tanh), maxPooling(2x2),
#              Dense, activation function(softmax)
#              Retraining with two models applied
#              Stochastic Conv(Mux+STanh(Adaptive)), Stochastic Dense(Normal mode)
# Cause:       Need short description for this file
# Initiator:   Junseok Oh
################################################################################
# File:		   intensive_snn_tests.py
# Version:     6.1 (SCR_V6.0-5)
# Author/Date: Junseok Oh / 2019-01-31
# Change:      Save the intermediate results in the txt format
#			   Refer to the following website
#			   https://stackoverflow.com/questions/3685265/how-to-write-a-multidimensional-array-to-a-text-file/3685295
# Cause:       Need to extract the intermediate results
# Initiator:   Florian Neugebauer
################################################################################
# File:		   intensive_snn_tests.py
# Version:     6.1 (SCR_V6.0-4)
# Author/Date: Junseok Oh / 2019-01-31
# Change:      Delete the object when it is not needed anymore
# Cause:       Need to handle the memory leakage issue during runtime
# Initiator:   Florian Neugebauer
################################################################################
# File:		   intensive_snn_tests.py
# Version:     6.0 (SCR_V5.4-2)
# Author/Date: Junseok Oh / 2019-01-05
# Change:      This software is branched from v6.0-PreV07-hybrid_cnn_passau.py
# Cause:       Intensive Stochastic Neural Network tests
# Initiator:   Florian Neugebauer
###############################################################################
import keras
from keras.datasets import mnist
from keras.models import Sequential, Model
from keras.layers import Dense, Dropout, Flatten, Activation
from keras.layers import Conv2D, MaxPooling2D
from keras import backend as K
from keras import regularizers
import WeightScaling_intensiveTests
from keras.utils.generic_utils import get_custom_objects
import numpy as np
from snn.holayer import HOModel, HOMaxPoolingExact, HOMaxPoolingAprox, HOConvolution, HOConnected
from snn.utils import HOUtils

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

get_custom_objects().update({'first_layer_activation': Activation(first_layer_activation)})

np.set_printoptions(threshold=np.inf)

batch_size = 128
num_classes = 10
epochs = 2

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
sentences = 'x_train shape: ' + str(x_train.shape)
print(x_train.shape[0], 'train samples')
sentences += '\n' + str(x_train.shape[0]) + ' train samples'
print(x_test.shape[0], 'test samples')
sentences += '\n' + str(x_test.shape[0]) + ' test samples'

# convert class vectors to binary class matrices
y_train = keras.utils.to_categorical(y_train, num_classes)
y_test = keras.utils.to_categorical(y_test, num_classes)
y_train = y_train[:60000]
y_test = y_test[:800]
print(y_train.shape)
sentences += '\n' + 'y_train shape: ' + str(y_train.shape)

if K.image_data_format() == 'channels_first':
    x_train = x_train.reshape(x_train.shape[0], 1, img_rows, img_cols)
    x_test = x_test.reshape(x_test.shape[0], 1, img_rows, img_cols)
    input_shape = (1, img_rows, img_cols)
else:
    x_train = x_train.reshape(x_train.shape[0], img_rows, img_cols, 1)
    x_test = x_test.reshape(x_test.shape[0], img_rows, img_cols, 1)
    input_shape = (img_rows, img_cols, 1)

# Binary NN for reference
model = Sequential()
model.add(Conv2D(4, kernel_size=(4, 4),
                 input_shape=input_shape,
                 use_bias=False,
                 kernel_regularizer=regularizers.l1(0.0007)))
model.add(Activation('first_layer_activation'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Flatten())
model.add(Dense(num_classes))
model.add(Activation('softmax'))

model.compile(loss=keras.losses.mse,
              optimizer=keras.optimizers.Adadelta(),
              metrics=['accuracy'])

#model.fit(x_train, y_train,
#          batch_size=batch_size,
#          epochs=epochs,
#          verbose=0,
#          callbacks=[WeightScaling_intensiveTests.WeightScale()],
#          validation_data=(x_test, y_test))
#model.save_weights('v8.0_test_result_IntensiveTests_19.h5')
model.load_weights('v8.0_test_result_IntensiveTests_19.h5')
score = model.evaluate(x_test[:500], y_test[:500], verbose=0)
print('1st Model results:')
sentences += '\n' + '1st Model results:'
print('Test loss:', score[0])
sentences += '\n' + 'Test loss: ' + str(score[0])
print('Test accuracy:', score[1])
sentences += '\n' + 'Test accuracy: ' + str(score[1])
score = model.evaluate(x_test[:107], y_test[:107], verbose=0)
print('Test loss:', score[0])
sentences += '\n' + 'Test loss: ' + str(score[0])
print('Test accuracy:', score[1])
sentences += '\n' + 'Test accuracy: ' + str(score[1])

layer1model = Model(inputs=model.input, outputs=model.get_layer(index=1).output)
layer2model = Model(inputs=model.input, outputs=model.get_layer(index=2).output)
layer3model = Model(inputs=model.input, outputs=model.get_layer(index=3).output)
layer4model = Model(inputs=model.input, outputs=model.get_layer(index=4).output)
layer5model = Model(inputs=model.input, outputs=model.get_layer(index=5).output)
layer6model = Model(inputs=model.input, outputs=model.get_layer(index=6).output)
#layer7model = Model(inputs=model.input, outputs=model.get_layer(index=7).output)
#layer8model = Model(inputs=model.input, outputs=model.get_layer(index=8).output)
#layer9model = Model(inputs=model.input, outputs=model.get_layer(index=9).output)


################### For debugging purpose, save the intermidiate results in the local variable ###################
# Predict the intermediate results from the Binary Neural Network
BNN_prediction = layer2model.predict(np.asarray([x_test[0]]))
txtTitle = 'v8.0_intensive_snn_tests48_conv_BNN_1st_model' + str(0 + 1) + '.txt'
with open(txtTitle, 'w') as outfile:
    # I'm writing a header here just for the sake of readability
    # Any line starting with "#" will be ignored by numpy.loadtxt
    outfile.write('# Array shape: {0}\n'.format(BNN_prediction[0].shape))

    # Iterating through a ndimensional array produces slices along
    # the last axis. This is equivalent to data[i,:,:] in this case
    for data_slice in BNN_prediction[0]:
        # The formatting string indicates that I'm writing out
        # the values in left-justified columns 7 characters in width
        # with 2 decimal places.
        np.savetxt(outfile, data_slice, fmt='%-7.3f')

        # Writing out a break to indicate different slices...
        outfile.write('# New slice\n')

del (BNN_prediction)
###################################################################################################################

# Generate the weights in txt format by using GetConvolutionLayerWeightsSN function
weights = model.get_layer(index=1).get_weights()[0]
txtTitle = 'v8.0_intensive_snn_tests48_weights1' + '.txt'
with open(txtTitle, 'w') as outfile:
    # I'm writing a header here just for the sake of readability
    # Any line starting with "#" will be ignored by numpy.loadtxt
    outfile.write('# Array shape: {0}\n'.format(weights.shape))
    outfile.write('{0}'.format(weights))
del(weights)

# Altering the weights from the 1st model
# Copy the weighs from the 1st model
weights = model.get_layer(index=1).get_weights()
del(model)

# Define the buffer of weights
tempListWeights = [[[] for i in range(4)] for i in range(4)]

# Copy the target sparse weights into the buffer
# Dimension: (col, row, inputSlice, outputSlice)
k=3
for i in range(4):
    for j in range(4):
        tempListWeights[i][j] = weights[0][i][j][0][k]

# Flatten the list using a nested list comprehension
listWeightsShuffled = [w for sublist in tempListWeights for w in sublist]

# Permute the weights in the list
listWeightsShuffled = np.random.permutation(listWeightsShuffled)

# Insert shuffled weights into the target
k=1
for i in range(4):
    for j in range(4):
        weights[0][i][j][0][k] = listWeightsShuffled[i*4+j]

################### For debugging purpose, save the weigts in txt format #######################################
txtTitle = 'altered weights.txt'
with open(txtTitle, 'w') as outfile:
    # I'm writing a header here just for the sake of readability
    # Any line starting with "#" will be ignored by numpy.loadtxt
    #outfile.write('# Array shape: {0}\n'.format(weights.shape))
    outfile.write('{0}'.format(weights))
################################################################################################################

# 2nd Model
epochs = 20
model2 = Sequential()
model2.add(Conv2D(4, kernel_size=(4, 4),
                 input_shape=input_shape,
                 use_bias=False,
                 kernel_regularizer=regularizers.l1(0.0007)))
model2.get_layer(index=1).set_weights(weights)
model2.add(Activation('first_layer_activation'))
model2.add(MaxPooling2D(pool_size=(2, 2)))
model2.add(Flatten())
model2.add(Dense(num_classes))
model2.add(Activation('softmax'))

model2.compile(loss=keras.losses.mse,
              optimizer=keras.optimizers.Adadelta(),
              metrics=['accuracy'])

#model2.fit(x_train, y_train,
#          batch_size=batch_size,
#          epochs=epochs,
#          verbose=0,
#          callbacks=[WeightScaling_intensiveTests.WeightScale()],
#          validation_data=(x_test, y_test))

#model2.save_weights('v8.0_test_result_IntensiveTests_38_20epochsOn2ndModel.h5')
model2.load_weights('v8.0_test_result_IntensiveTests_38_20epochsOn2ndModel.h5')
score = model2.evaluate(x_test[:500], y_test[:500], verbose=0)
print('2nd Model results:')
sentences += '\n' + '2nd Model results:'
print('Test loss:', score[0])
sentences += '\n' + 'Test loss: ' + str(score[0])
print('Test accuracy:', score[1])
sentences += '\n' + 'Test accuracy: ' + str(score[1])
score = model2.evaluate(x_test[:107], y_test[:107], verbose=0)
print('Test loss:', score[0])
sentences += '\n' + 'Test loss: ' + str(score[0])
print('Test accuracy:', score[1])
sentences += '\n' + 'Test accuracy: ' + str(score[1])

layer1model = Model(inputs=model2.input, outputs=model2.get_layer(index=1).output)
layer2model = Model(inputs=model2.input, outputs=model2.get_layer(index=2).output)
layer3model = Model(inputs=model2.input, outputs=model2.get_layer(index=3).output)
layer4model = Model(inputs=model2.input, outputs=model2.get_layer(index=4).output)
layer5model = Model(inputs=model2.input, outputs=model2.get_layer(index=5).output)
layer6model = Model(inputs=model2.input, outputs=model2.get_layer(index=6).output)
#layer7model = Model(inputs=model.input, outputs=model.get_layer(index=7).output)
#layer8model = Model(inputs=model.input, outputs=model.get_layer(index=8).output)
#layer9model = Model(inputs=model.input, outputs=model.get_layer(index=9).output)


################### For debugging purpose, save the intermidiate results in the local variable ###################
# Predict the intermediate results from the Binary Neural Network
BNN_prediction = layer2model.predict(np.asarray([x_test[0]]))
txtTitle = 'v8.0_intensive_snn_tests48_conv_BNN_2nd_model' + str(0 + 1) + '.txt'
with open(txtTitle, 'w') as outfile:
    # I'm writing a header here just for the sake of readability
    # Any line starting with "#" will be ignored by numpy.loadtxt
    outfile.write('# Array shape: {0}\n'.format(BNN_prediction[0].shape))

    # Iterating through a ndimensional array produces slices along
    # the last axis. This is equivalent to data[i,:,:] in this case
    for data_slice in BNN_prediction[0]:
        # The formatting string indicates that I'm writing out
        # the values in left-justified columns 7 characters in width
        # with 2 decimal places.
        np.savetxt(outfile, data_slice, fmt='%-7.3f')

        # Writing out a break to indicate different slices...
        outfile.write('# New slice\n')

del (BNN_prediction)
###################################################################################################################

# Generate the weights in txt format by using GetConvolutionLayerWeightsSN function
weights = model2.get_layer(index=1).get_weights()[0]
txtTitle = 'v8.0_intensive_snn_tests48_weights2' + '.txt'
with open(txtTitle, 'w') as outfile:
    # I'm writing a header here just for the sake of readability
    # Any line starting with "#" will be ignored by numpy.loadtxt
    outfile.write('# Array shape: {0}\n'.format(weights.shape))
    outfile.write('{0}'.format(weights))
del(weights)

# Hybrid NN with stochastic convolutional layer and binary dense layer

# SN length
length = 1024*4
#length = 1024*4

ut = HOUtils()

# weights and biases of the convolutional layer
#bias_SNs = ut.GetConvolutionLayerBiasesSN(model, 1, length)
weight_SNs, listIndex = ut.GetConvolutionLayerWeightsSN(model2, 1, length)

# weights and biases of dense layer
dense_biases = ut.GetConnectedLayerBiases(model2, 5)
dense_weight_SNs = ut.GetConnectedLayerWeightsSN(model2, 5, length)

#SN_input_matrix = np.full((img_rows, img_cols, length), False)

output = np.zeros((1, 10))
correct_predictions = 0

test_index = 0

output_mse = 0

print('start stochastic NN')
sentences += '\n' + 'start stochastic NN'
# for each input in the test set
for r in range(100):
    x = x_test[test_index]
    print(test_index)
    sentences += '\n' + 'test case ' + str(test_index+1)

    # build input SN matrix
    SN_input_matrix = np.full((img_rows, img_cols, length), False)
    for i in range(img_rows):
        for j in range(img_cols):
            SN_input_matrix[i, j] = createSN(x[0, i, j], length)
    del(x)
    print('inputs generated')
    sentences += '\n' + 'inputs generated'

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
    sentences += '\n' + 'conv layer done'

    if(test_index % 10 == 0):
        ut.SaveInTxtFormat('v8.0_intensive_snn_tests48_conv', test_index,
                           hoModel.GetOutputMatrix(), 4, 25, 25,
                           layer2model, x_test)
        print(str(test_index+1)+' conv layer results saved in txt format')
        sentences += '\n' + str(test_index+1)+' conv layer results saved in txt format'

    # max pooling layer
    hoMaxLayer = HOMaxPoolingExact(2, 2, length)
    hoModel.Activation(hoMaxLayer, stride=2) # Stride:2, filterSize:2x2
    del(hoMaxLayer)
    print("maxpool layer done")
    sentences += '\n' + 'maxpool layer done'
    if(test_index % 10 == 0):
        ut.SaveInTxtFormat('v8.0_intensive_snn_tests48_maxpool', test_index,
                           hoModel.GetOutputMatrix(), 4, 12, 12,
                           layer3model, x_test)
        print(str(test_index+1)+' maxpool layer results saved in txt format')
        sentences += '\n' + str(test_index+1)+' conv layer results saved in txt format'

    # First dense layer
    hoModel.SetDenseWeights(dense_weight_SNs)
    hoModel.SetDenseBias(dense_biases)
    hoDenseLayer = HOConnected(length, stochToInt="Normal", activationFunc="None")
    hoModel.Activation(hoDenseLayer, num_classes=num_classes)
    del(hoDenseLayer)
    ################### For debugging purpose, save the intermidiate results in the local variable ###################
    dense_output = hoModel.GetOutputMatrix()
    print("dense 1 output from Binary NN")
    sentences += '\n' + 'dense 1 output from Binary NN'
    BNN_prediction = layer5model.predict(np.asarray([x_test[test_index]]))
    print(BNN_prediction)
    sentences += '\n' + str(BNN_prediction)
    del(BNN_prediction)
    print("dense 1 output from Stochastic NN")
    sentences += '\n' + 'dense 1 output from Stochastic NN'
    print(dense_output)
    sentences += '\n' + str(dense_output)
    ################################################################################################################
    print('dense 1 layer done')
    sentences += '\n' + 'dense 1 layer done'

    out_error = 0
    out = layer5model.predict(np.asarray([x_test[test_index]]))
    for i in range(10):
        out_error = out_error + (dense_output[0, i] - out[0, i])**2

    print("out_error:", out_error)
    sentences += '\n' + 'out_error: '+str(out_error)
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
    sentences += '\n' + 'current_accuracy: '+str(current_accuracy)

    del(dense_output)
    del(hoModel)

correct_predictions = correct_predictions/100
print("correct classifications:", correct_predictions)
sentences += '\n' + 'correct classifications: '+str(correct_predictions)
output_mse = output_mse/100
print("output_mse:", output_mse)
sentences += '\n' + 'output_mse: '+str(output_mse)


################### For debugging purpose, save the weigts in txt format #######################################
txtTitle = 'v8.0_Intensive_snn_tests48.txt'
with open(txtTitle, 'w') as outfile:
    # I'm writing a header here just for the sake of readability
    # Any line starting with "#" will be ignored by numpy.loadtxt
    #outfile.write('# Array shape: {0}\n'.format(weights.shape))
    outfile.write('{0}'.format(sentences))
################################################################################################################