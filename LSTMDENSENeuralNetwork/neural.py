import numpy
from sklearn.model_selection import train_test_split
from tensorflow.python.keras.layers import LSTM, Dense
from tensorflow.python.keras.utils.np_utils import to_categorical
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.callbacks import TensorBoard
import Queries as qr


def getNetworkLogs():
    logs = TensorBoard(log_dir="Logs")
    return logs


def prepareOutputShape():
    actions = qr.getAllActions()
    actionDictionary = dict()
    for i, action in enumerate(actions):
        actionDictionary[action] = i

    videoShape = []
    videoDictionary = []
    for action in actions:
        videos = qr.getVideosID(action)
        for video in videos:
            videoData = qr.getVideoFrameData(video)
            videoShape.append(videoData)
            videoDictionary.append(actionDictionary[action])
    videoShape = numpy.array(videoShape)
    return actionDictionary, videoShape, videoDictionary


def getTestPortion():
    dummy, x, y = prepareOutputShape()
    y = to_categorical(y).astype(int)
    trainX, testX, trainY, testY = train_test_split(x, y, test_size=0.1)
    return trainX, testX, trainY, testY


def trainNeuralNetwork():
    seqModel = Sequential()
    actions = qr.getAllActions()
    seqModel.add(LSTM(units=64, return_sequences=True, input_shape=(30, 258), activation="relu"))
    seqModel.add(LSTM(units=128, return_sequences=True, activation="relu"))
    seqModel.add(LSTM(units=64, return_sequences=False, activation="relu"))
    seqModel.add(Dense(units=64, activation="relu"))
    seqModel.add(Dense(units=32, activation="relu"))
    # softmax activation returns an array of probabilities that add up to 1
    seqModel.add(Dense(len(actions), activation="softmax"))  # last layer units represents the shape of the output we need
    seqModel.compile(optimizer="Adam", loss="categorical_crossentropy", metrics=["categorical_accuracy"])  # remove metrics
    trainX, testX, trainY, testY = getTestPortion()
    seqModel.fit(trainX, trainY, epochs=200, callbacks=[getNetworkLogs()])
    seqModel.save("actionWeights.h5")


# trainNeuralNetwork()