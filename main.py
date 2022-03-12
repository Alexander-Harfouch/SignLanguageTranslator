import mediapipe as mdp
import cv2
import numpy


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

    for landmarks in processedFrame.right_hand_landmarks.landmark:  # loop over all right-hand landmarks
        if processedFrame.right_hand_landmarks:  # if landmark exists
            rightHandLandmarks.append(numpy.array([landmarks.x, landmarks.y, landmarks.z]).flatten())  # add landmark
        else:
            rightHandLandmarks.append(numpy.zeros(63))  # add array of zeros as replacement for landmark

    for landmarks in processedFrame.left_hand_landmarks.landmark:
        if processedFrame.left_hand_landmarks:
            leftHandLandmarks.append(numpy.array([landmarks.x, landmarks.y, landmarks.z]).flatten())
        else:
            leftHandLandmarks.append(numpy.zeros(63))

    for landmarks in processedFrame.pose_landmarks.landmark:
        if processedFrame.pose_landmarks:
            poseLandmarks.append(numpy.array([landmarks.x, landmarks.y, landmarks.z, landmarks.visibility]).flatten())
        else:
            poseLandmarks.append(numpy.zeros(132))

    #  concatenate all arrays into 1 array and return
    return numpy.concatenate([rightHandLandmarks, leftHandLandmarks, poseLandmarks])


callCaptureLoop()