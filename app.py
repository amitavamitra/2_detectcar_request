from flask import Flask,render_template,Response,session, redirect , json
from flask_pymongo import PyMongo
from flask_mail import Mail, Message
import flask
import numpy
from dotenv import load_dotenv
import os
load_dotenv()
import cv2
import pytesseract
from matplotlib import pyplot as plt
import numpy as np
# import pytesseract
import pandas as pd
import datetime
from fuzzywuzzy import fuzz
from fuzzywuzzy import process


app=Flask(__name__)

# https://pythonbasics.org/flask-mail/
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'amitavamitrasap@gmail.com'
app.config['MAIL_PASSWORD'] = os.environ.get("PASSWORD")
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

# @app.route("/")

def send_mail(name):
    email = 'amitavamitrasap@gmail.com'
    name = name
    message = "\r\n  What are you thinking about lunch today. Please state your choice and save the planet, by reducing waste.\r\n Please sign up at this app  https://lunch-intelligent-lemur-yh.cfapps.eu10.hana.ondemand.com/. \r\n Certainty help us procure your ingredients from locally produced sustainable sources. So if you can plan your lunch for a month would not only be healthy for you but also for the planet. \r\n With Love and Care  , \r\n Your Canteen awaits you." 
    msg = Message("Message from your canteen",
                  
                  sender=email,
                  recipients=["amitavamitrasap@gmail.com"])
    msg.body = 'Hi ' +  name + message
    mail.send(msg)
    return "Sent"

# https://stackoverflow.com/questions/21133976/flask-load-local-json

@app.route("/readjson")
# static/data/car_db.json
def readjson():
    filename = os.path.join(app.static_folder, 'data', 'car_db.json')
    with open(filename) as f:
        data = json.load(f)
        print('*******************************car database***********************')
        print(data)
        print('*******************************car database***********************')
    return render_template('index.html', data=data)


app.config["MONGO_URI"] = "mongodb://localhost:27017/carDB"
mongodb_client = PyMongo(app)
db = mongodb_client.db

@app.route("/car_add")
def add_many():
    filename = os.path.join(app.static_folder, 'data', 'car_db.json')
    with open(filename) as f:
        data = json.load(f)
    db.car.insert_many(data)
    return ("successfully added all cars to db")



# Read the Employee and Car Registration DB
app.config["MONGO_URI"] = MONGO_URL='mongodb://localhost:27017/registry'
mongodb_client = PyMongo(app)
db = mongodb_client.db

@app.route("/registry")
def finall():
    images = db.images.find()
    """
    Returns list of all genres in the database.
    """
      
    return  json.dumps([image for image in images])

data =[]
df = pd.DataFrame(data, columns=['col', 'Name', 'email'])

df1 = pd.read_csv('car_reg.csv')
img_counter = 0
cntr = 0
camera=cv2.VideoCapture(0)


def generate_frames():
    global img_counter
    global cntr
    while True:
            
        ## read the camera frame
        success,frame=camera.read()
        if not success:
            break
        else:
            ret,buffer=cv2.imencode('.jpg',frame)
            retu , img = camera.read()
            frame=buffer.tobytes()
            
            from fuzzywuzzy import fuzz
            from fuzzywuzzy import process

            # Bounding box attempt- performance issue!!
            # cntr = cntr + 1
            # if((cntr%20==0)):
            #     imgH , imgW , _ = img.shape
            #     x1,y1,w1,h1 = 0,0, imgH,imgW
            #     imgChar = pytesseract.image_to_string(img)
            #     imgboxes = pytesseract.image_to_boxes(img)
            #     for boxes in imgboxes.splitlines():
            #         boxes = boxes.split(' ')
            #         x,y,w,h = int(boxes[1]),int(boxes[2]),int(boxes[3]),int(boxes[4])
            #         cv2.rectangle(img, (x , imgH-y), (w,imgH-h),(0,0,255),3)
            #     cv2.putText(img, imgChar , (75, 50) , cv2.FONT_HERSHEY_COMPLEX, 0.7, (0,255,255),2)
            #     font = cv2.FONT_HERSHEY_SIMPLEX
            #     x = cv2.imshow("Tracking Text", img)
            # 
            # pytesseract.pytesseract.tesseract_cmd = r'C:\Users\I304524\AppData\Local\Tesseract-OCR\tesseract.exe'
            # This pytesseract needs to be changed only in case of docker for correct path.
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            text = pytesseract.image_to_string(img, config='-l eng --oem 1 --psm 6')
            print('********************Pytesseract OCR reading from the image capture ********************')
            print(text)
            # print('********************car registration database*******************************************')
            df1 = pd.read_csv('car_reg.csv')
            print(df1)
            carReg = df1['col']
            # The camera gets more than the number plate.Hence we get a string at one hand
            # which needs to be fuzzy-matched to the plates in the car registration db
            # Levensthein distance implementation in fuzzywuzzy gives a simple solution
            print('**************************Levensthein distance*******************************************')

            leastDistance = []
            for car in carReg:
                str1 = car
                # print(fuzz.partial_ratio(str1,text))
                leastDistance.append(fuzz.partial_ratio(str1,text))
            print('*****************Car belongs to ?? **************************')
            print(leastDistance)
            x = np.argmax(leastDistance)
            print(x)
            if max(leastDistance) !=0:
                ct = datetime.datetime.now()
                # print(df1.loc[x] , ct)
                print('***************dataframe*********************')
                carOwner = df1.loc[x].Name
                print(carOwner)
                print('***************dataframe*********************')
                # data = [df1.loc[x],ct]
                # For a perfect match take a snap and send the email ?
                if max(leastDistance) == 100:
                    
                    now = datetime.datetime.now()
                    img_name = "car_plate_{}.png".format(img_counter)
                    cv2.imwrite('images/' + img_name, img)
                    print("{} written!".format(img_name))
                    img_counter += 1
                    # https://stackoverflow.com/questions/34122949/working-outside-of-application-context-flask
                    with app.app_context():
                        send_mail(carOwner)
                    

            else:
                print('No match was found')
        # frame sent to the browser  
        yield(b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# https://stackoverflow.com/questions/52644035/how-to-show-a-pandas-dataframe-into-a-existing-flask-html-table

@app.route('/')
def index():
    
    generate_frames()
    # return render_template('index.html' , headings=headings , data=(df1.loc[x],ct))
    return render_template('index.html',  tables=[df.to_html(classes='data')], titles=df.columns.values)
    

@app.route('/mission')
def mission():
    return render_template('mission.html')


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/it')
def it():
    return render_template('it.html')

# @app.route('/mission')
# def mission():
#     return render_template('mission.html')

# Since we have no authentication or trust at this stage.. this is commented out..
# @app.route('/about')
# def about():
#     return requests.get('https://innovatorchallenge-prod-iclandingpageui.cfapps.eu10.hana.ondemand.com/uimodule/index.html?tab=team').content


@app.route('/video')
def video():
    return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')
# https://stackoverflow.com/questions/30136257/how-to-get-image-from-video-using-opencv-python

if __name__=="__main__":
    app.run(debug=True)


