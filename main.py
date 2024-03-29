import mediapipe as mdp
import cv2
import numpy
import Queries as qr
import tensorflow as tf


def interpretActions():
    frames = []
    word = ""
    seqModel = tf.keras.models.load_model('LSTMDENSENeuralNetwork/actionWeights.h5')
    actions = qr.getAllActions()
    videoCapture = cv2.VideoCapture(0)  # launch camera, parameter might change between different machines
    pipeModel = mdp.solutions.holistic  # create UNPROCESSED virtual model
    pipeModelHolistic = pipeModel.Holistic(min_detection_confidence=0.5,
                                           min_tracking_confidence=0.5)  # create detector and tracker
    modelDrawing = mdp.solutions.drawing_utils  # get model drawing tools
    while videoCapture.isOpened():  # loop until camera closes
        dummy, currentFrame = videoCapture.read()  # get current frame
        processedFrame, currentFrame = processCurrentFrame(currentFrame, pipeModelHolistic)  # get processed frame
        frames.insert(0, createLandmarkArrays(processedFrame))
        drawKeyPoints(currentFrame, processedFrame, pipeModel, modelDrawing)  # draw virtual model
        frames = frames[:30]
        prediction = [0]
        if len(frames) == 30:  # if we have 30 frames
            prediction = seqModel.predict(numpy.expand_dims(frames, axis=0))[0].tolist()  # make prediction

        if prediction.index(max(prediction)) > 0.95:  # if prediction is valid
            if actions[prediction.index(max(prediction))] != word:  # if prediction is different from prev
                word = actions[prediction.index(max(prediction))]
        else:
            word = actions[prediction.index(max(prediction))]

        cv2.rectangle(currentFrame, (0, 0), (640, 60), (10, 10, 10), -1)
        cv2.putText(currentFrame, " ".join(str(word).replace("(", "").replace(")", "").replace(",", "").replace("'", ""))
                    , (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
        cv2.imshow("Sign Language Translator", currentFrame)  # show video being rendered
        if cv2.waitKey(1) & 0xFF == ord(' '):  # exit loop if space is pressed
            break
    videoCapture.release()  # close camera
    cv2.destroyAllWindows()  # close window pop up


def callCaptureLoop():
    videoCapture = cv2.VideoCapture(0)  # launch camera, parameter might change between different machines
    pipeModel = mdp.solutions.holistic  # create UNPROCESSED virtual model
    pipeModelHolistic = pipeModel.Holistic(min_detection_confidence=0.5,
                                           min_tracking_confidence=0.5)  # create detector and tracker
    modelDrawing = mdp.solutions.drawing_utils  # get model drawing tools
    while videoCapture.isOpened():  # loop until camera closes
        dummy, currentFrame = videoCapture.read()  # get current frame
        processedFrame, currentFrame = processCurrentFrame(currentFrame, pipeModelHolistic)  # get processed frame
        createLandmarkArrays(processedFrame)
        drawKeyPoints(currentFrame, processedFrame, pipeModel, modelDrawing)  # draw virtual model
        cv2.imshow("Sign Language Translator", currentFrame)  # show video being rendered
        if cv2.waitKey(1) & 0xFF == ord(' '):  # exit loop if space is pressed
            break
    videoCapture.release()  # close camera
    cv2.destroyAllWindows()  # close window pop up


def insertAction(Action_Name):
    qr.prepareAction(Action_Name)
    videoCapture = cv2.VideoCapture(0)  # launch camera, parameter might change between different machines
    pipeModel = mdp.solutions.holistic  # create UNPROCESSED virtual model
    pipeModelHolistic = pipeModel.Holistic(min_detection_confidence=0.5,
                                           min_tracking_confidence=0.5)  # create detector and tracker
    modelDrawing = mdp.solutions.drawing_utils  # get model drawing tools
    Videos_ID = qr.getVideosID(Action_Name)
    for video in range(30):
        for frame in range(30):
            dummy, currentFrame = videoCapture.read()  # get current frame
            processedFrame, currentFrame = processCurrentFrame(currentFrame, pipeModelHolistic)  # get processed frame
            createLandmarkArrays(processedFrame)
            drawKeyPoints(currentFrame, processedFrame, pipeModel, modelDrawing)  # draw virtual model

            if frame == 0:
                cv2.putText(currentFrame, "GET READY", (150, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                cv2.imshow("Sign Language Translator", currentFrame)
                cv2.waitKey(1000)
            else:
                cv2.putText(currentFrame, f"Frame: {frame} Video: {video} Action: {Action_Name}",
                            (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                cv2.imshow("Sign Language Translator", currentFrame)

            landmarks = createLandmarkArrays(processedFrame)
            qr.insertFrame(landmarks, Videos_ID[video])  # add frame to database
            cv2.imshow("Sign Language Translator", currentFrame)  # show video being rendered
            if cv2.waitKey(1) & 0xFF == ord(' '):  # exit loop if space is pressed
                break
    videoCapture.release()  # close camera
    cv2.destroyAllWindows()  # close window pop up


# the holistic function "process" requires an image to be in RGB. OpenCV gives a BRG image, so we convert it to RGB
def processCurrentFrame(currentFrame, pipeModelHolistic):
    currentFrame = cv2.cvtColor(currentFrame, cv2.COLOR_BGR2RGB)  # converts frame's color configuration to RGB
    processedFrame = pipeModelHolistic.process(currentFrame)  # processes the frame
    currentFrame = cv2.cvtColor(currentFrame, cv2.COLOR_RGB2BGR)  # converts frame back to BGR
    return processedFrame, currentFrame


def drawKeyPoints(currentFrame, processedFrame, pipeModel, modelDrawing):
    connections = modelDrawing.DrawingSpec(thickness=1)  # new keypoint connections format
    keyPoints = modelDrawing.DrawingSpec(circle_radius=3, color=(0, 0, 255), thickness=2)  # new key points format
    modelDrawing.draw_landmarks(currentFrame, processedFrame.right_hand_landmarks, pipeModel.HAND_CONNECTIONS,
                                keyPoints, connections)  # draw right hand
    modelDrawing.draw_landmarks(currentFrame, processedFrame.left_hand_landmarks, pipeModel.HAND_CONNECTIONS,
                                keyPoints, connections)  # draw left hand
    modelDrawing.draw_landmarks(currentFrame, processedFrame.pose_landmarks, pipeModel.POSE_CONNECTIONS,
                                keyPoints, connections)  # draw upper torso, nose, eyes, mouth
    modelDrawing.draw_landmarks(currentFrame, processedFrame.face_landmarks, pipeModel.FACEMESH_CONTOURS,
                                modelDrawing.DrawingSpec(circle_radius=1, color=(255, 0, 50), thickness=1),
                                connections)  # draw face


def createLandmarkArrays(processedFrame):
    rightHandLandmarks = []
    leftHandLandmarks = []
    poseLandmarks = []

    if processedFrame.right_hand_landmarks:  # if landmark exists
        for landmarks in processedFrame.right_hand_landmarks.landmark:  # loop over all right-hand landmarks
            rightHandLandmarks.extend(numpy.array([landmarks.x, landmarks.y, landmarks.z]).flatten())  # add landmark
    else:
        rightHandLandmarks.extend(numpy.zeros(63))  # add array of zeros as replacement for landmark

    if processedFrame.left_hand_landmarks:
        for landmarks in processedFrame.left_hand_landmarks.landmark:
            leftHandLandmarks.extend(numpy.array([landmarks.x, landmarks.y, landmarks.z]).flatten())
    else:
        leftHandLandmarks.extend(numpy.zeros(63))

    if processedFrame.pose_landmarks:
        for landmarks in processedFrame.pose_landmarks.landmark:
            poseLandmarks.extend(numpy.array([landmarks.x, landmarks.y, landmarks.z, landmarks.visibility]).flatten())
    else:
        poseLandmarks.extend(numpy.zeros(132))

    #  concatenate all arrays into 1 array and return
    return numpy.concatenate([rightHandLandmarks, leftHandLandmarks, poseLandmarks]).tolist()
