import numpy
import psycopg2


def connect():
    return psycopg2.connect(
        database="postgres",
        user="postgres",
        password="root",
        port="5050"
    )


def prepareAction(name):
    con = connect()
    cursor = con.cursor()
    cursor.execute('truncate table "SActions", "SVideos", "SFrames" RESTART IDENTITY')
    cursor.execute('INSERT INTO "SActions" ("Action_Name") values (%s)', (name,))
    cursor.execute('SELECT "Action_ID" FROM "SActions" WHERE "Action_Name" = %s', (name,))
    actionID = cursor.fetchone()
    for i in range(30):
        cursor.execute('INSERT INTO "SVideos" ("Action_ID") values (%s)', (actionID,))
    con.commit()
    con.close()


def insertFrame(Frame_Data, Video_ID):
    con = connect()
    cursor = con.cursor()
    cursor.execute('INSERT INTO "SFrames" ("Video_ID", "Frame_Data") values (%s, %s)', (Video_ID, Frame_Data))
    con.commit()
    con.close()


def getAllActions():
    con = connect()
    cursor = con.cursor()
    cursor.execute('SELECT "Action_Name" FROM "SActions"')
    actions = cursor.fetchall()
    return actions


def getActionID(Action_Name):
    con = connect()
    cursor = con.cursor()
    cursor.execute('SELECT "Action_ID" FROM "SActions" WHERE "Action_Name" = %s', (Action_Name,))
    name = cursor.fetchone()
    con.close()
    return name


def getVideosID(Action_Name):
    con = connect()
    cursor = con.cursor()
    actionID = getActionID(Action_Name)
    cursor.execute('SELECT "Video_ID" FROM "SVideos", "SActions" WHERE "SActions"."Action_ID" = "SVideos"."Action_ID"'
                   ' and "SActions"."Action_ID" = %s', (actionID,))
    Video_IDs = cursor.fetchall()
    con.close()
    return Video_IDs


def deleteAction(Action_Name):
    con = connect()
    cursor = con.cursor()
    actionID = getActionID(Action_Name)
    cursor.execute('DELETE FROM "SActions" WHERE "Action_ID" = %s', (actionID, ))
    cursor.close()
    con.commit()
    con.close()


def getVideoFrameData(videoID):
    con = connect()
    cursor = con.cursor()
    cursor.execute('SELECT "Frame_Data" FROM "SFrames" WHERE "Video_ID" = %s', (videoID, ))
    framesData = cursor.fetchall()

    parseFrames = []
    for frame in framesData:
        parseFrames.extend(list(frame))
    framesData = numpy.array(parseFrames)
    cursor.close()
    con.close()
    return framesData


def prepareDemoAction(name):
    con = connect()
    cursor = con.cursor()
    # cursor.execute('truncate table "SActions", "SVideos", "SFrames" RESTART IDENTITY')
    cursor.execute('INSERT INTO "SActions" ("Action_Name") values (%s)', (name,))
    cursor.execute('SELECT "Action_ID" FROM "SActions" WHERE "Action_Name" = %s', (name,))
    actionID = cursor.fetchone()
    for i in range(30):
        cursor.execute('INSERT INTO "SVideos" ("Action_ID") values (%s)', (actionID,))
    con.commit()

    videosID = getVideosID(name)
    demoFrame = numpy.zeros(258).tolist()
    for j in range(30):
        for z in range(30):
            insertFrame(demoFrame, videosID[j])
    con.commit()
    con.close()

# prepareDemoAction("test1")
# print("finished test1")
# prepareDemoAction("test2")
# print("finished test2")
# prepareDemoAction("test3")
# print("finished test3")