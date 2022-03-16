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
    # cursor.execute('truncate table "SActions", "SVideos", "SFrames" RESTART IDENTITY')
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
