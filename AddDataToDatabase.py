import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://faceattendance-98eec-default-rtdb.firebaseio.com/"
})

ref = db.reference('Students')

data = {
    "11111":
        {
            "name": "Elon Musk",
            "major": "Physics",
            "starting_year": 2025,
            "total_attendance": 6,
            "standing": "G",
            "year": 4,
            "last_attendace_time": "2025-10-15 00:22:30"
        },
    "22222":
        {
            "name": "Vishal Ipar",
            "major": "Machine Learning",
            "starting_year": 2024,
            "total_attendance": 8,
            "standing": "G",
            "year": 4,
            "last_attendace_time": "2025-10-13 04:20:32"
        },
    "33333":
        {
            "name": "Sunita Villiams",
            "major": "Aeronautics",
            "starting_year": 2023,
            "total_attendance": 3,
            "standing": "G",
            "year": 3,
            "last_attendace_time": "2025-10-14 10:24:20"
        },
    "44444":
        {
            "name": "Mark Zuckerberg",
            "major": "Facebook",
            "starting_year": 2006,
            "total_attendance": 4,
            "standing": "B",
            "year": 2,
            "last_attendace_time": "2025-10-14 10:24:20"
        },
}

for key, value in data.items():
    ref.child(key).set(value)