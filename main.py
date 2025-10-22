import cv2
import cvzone
import face_recognition
import numpy as np
import os
import pickle
import firebase_admin
from firebase_admin import db, credentials
import cloudinary
import cloudinary.api
import urllib
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# cloudinary configuration
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

# Initialiaze firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://faceattendance-98eec-default-rtdb.firebaseio.com/"
})

cap = cv2.VideoCapture(0)
cap.set(3, 662)
cap.set(4, 418)


imgBackground = cv2.imread('resources/background1.png')

# Importing mode images to the list
folderModePath = 'resources/modes'
modePathList = os.listdir(folderModePath)
imgModeList = [] # Add full image mode paths to this list

for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

# load the encoding file
file = open('EncodeFile.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds
# print(studentIds)

modeType = 0
counter = 0
id = -1
imgStudent = []

while True:
    ret, img = cap.read()
    img = cv2.resize(img, (662,418))

    imgS = cv2.resize(img, (0,0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    imgBackground[200:200+418, 62:62+662] = img
    imgBackground[60:60+597, 885:885+353] = imgModeList[modeType]

    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            # print('matches' , matches)
            # print('Distance', faceDis)

            matchIndex = np.argmin(faceDis)
            # print('Match index :', matchIndex)

            if matches[matchIndex]:
                # print('Known face detected .')
                # print(studentIds[matchIndex])
                y1,x2,y2,x1 = faceLoc
                y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
                bbox = 55 + x1, 162+y1, x2-x1, y2-y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                id = studentIds[matchIndex]

                if counter == 0:
                    cvzone.putTextRect(imgBackground, 'Loading', (295, 420))
                    cv2.imshow('Face Attendance', imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1

        if counter != 0:
            if counter == 1:
                studentInfo = db.reference(f'Students/{id}').get()
                # print(studentInfo)
                # get image from cloudinary
                cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
                extensions = ['png', 'jpg', 'jpeg']
                for ext in extensions:
                    try:
                        img_url = f'https://res.cloudinary.com/{cloud_name}/image/upload/images/{id}.{ext}'
                        # print('Trying url :',img_url)
                        # Download image as byte
                        req = urllib.request.urlopen(img_url)
                        array = np.asarray(bytearray(req.read()), dtype=np.uint8)
                        # Decode to opencv image
                        imgStudent = cv2.imdecode(array, cv2.IMREAD_COLOR)

                    except:
                        continue

                # Update data of attendance
                datetimeobject = datetime.strptime(studentInfo['last_attendace_time'],
                                                   "%Y-%m-%d %H:%M:%S")
                secondsElapsed = (datetime.now()-datetimeobject).total_seconds()
                # print(secondsElapsed)
                if secondsElapsed > 20:
                    ref = db.reference(f'Students/{id}')
                    studentInfo['total_attendance'] += 1
                    ref.child('total_attendance').set(studentInfo['total_attendance'])
                    ref.child('last_attendace_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 3
                    counter = 0
                    imgBackground[60:60 + 597, 885:885 + 353] = imgModeList[modeType]

            if modeType != 3:
                if 10 < counter < 20:
                    modeType = 2
                imgBackground[60:60 + 597, 885:885 + 353] = imgModeList[modeType]

                if counter <= 10:
                    cv2.putText(imgBackground, str(studentInfo['total_attendance']),(948,127),
                                cv2.FONT_HERSHEY_SIMPLEX,1, (255,255,255),2)
                    cv2.putText(imgBackground, str(studentInfo['major']), (1029,550),cv2.FONT_HERSHEY_COMPLEX,
                                0.5,(255,255,255),1)
                    cv2.putText(imgBackground, str(id), (1029,496), cv2.FONT_HERSHEY_COMPLEX,
                                0.5,(255,255,255),1)
                    cv2.putText(imgBackground, str(studentInfo['standing']), (958,620), cv2.FONT_HERSHEY_COMPLEX,
                                0.6, (100,100,100),1)
                    cv2.putText(imgBackground, str(studentInfo['year']), (1070,620), cv2.FONT_HERSHEY_COMPLEX,
                                0.6, (100,100,100),1)
                    cv2.putText(imgBackground, str(studentInfo['starting_year']), (1170,620), cv2.FONT_HERSHEY_COMPLEX,
                                0.6, (100,100,100), 1)

                    (w,h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX,1,1)
                    offset = (353-w)//2
                    cv2.putText(imgBackground, str(studentInfo['name']), (885+offset, 445), cv2.FONT_HERSHEY_COMPLEX,
                                1, (50, 50, 50), 1)

                    imgBackground[169:169+230, 947:947+230] = imgStudent

                counter+=1

                if counter >= 20:
                    counter = 0
                    modeType = 0
                    studentInfo = []
                    imgStudent = []
                    imgBackground[60:60+597, 885:885+353] = imgModeList[modeType]

    else:
        modeType = 0
        counter = 0

    #cv2.imshow('Webcam', img)
    cv2.imshow('Face Attendance', imgBackground)
    cv2.waitKey(1)