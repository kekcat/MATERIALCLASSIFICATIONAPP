from ast import Return
from flask import Flask, render_template, Response, request
from classification import classify
import cv2
import os

global typedata
typedata = 0
global capture
capture = 0
global matlist
matlist = {0: 'wood.html', 1: 'steel.html'}
global matload
matload = ''
global pageDec
pageDec = ''
global pictaken
pictaken = False
global globaltempath
globaltempath = 'materialPages/'


try:
    os.mkdir('./Photos')
except OSError as error:
    pass


app = Flask(__name__, template_folder='./templates')
camera = cv2.VideoCapture(0)


def gen_frames():
    global capture
    global typedata
    global pageDec
    global pictaken
    global globaltempath
    
    while True:
        success, frame = camera.read()

        if success:

            if capture:
                capture = 0
                p = 'flaskr/Photos/shot.png'
                cv2.imwrite(p, frame)

                typedata = classify()

                pageDec = typedata['prediction'].lower()
                pageDec = f"{globaltempath}{typedata['prediction'].lower()}/{pageDec}.html"
                pictaken = True
                print(pageDec)
                    
            try:
                ret, buffer = cv2.imencode('.jpg', cv2.flip(frame, 1))
                frame = buffer.tobytes()

                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

            except Exception as e:
                pass

        else:
            pass


@app.route('/')
def index():
    global typedata
    global page

    page = ''
    typedata = {}
    
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/requests',methods=['POST','GET'])
def tasks():
    global camera
    global typedata
    global pageDec
    global pictaken
    global globaltempath

    if request.method == 'POST':

        if request.form.get('mat'):
            matPage = request.form.get('mat')

            page = f"{globaltempath}{matPage}/{matPage.lower()}2.html"
            return render_template(page)
        
        if request.form.get('click') == 'Capture':
            global capture
            print("Pic taken")
            capture = 1
            pictaken = True

        if request.form.get('click') == "To Info":
            if pictaken == True:
                pictaken = False
                return render_template(pageDec, data=typedata)

            else:
                return render_template("nomat.html")


    elif request.method == 'GET':
        return render_template('index.html')
    return render_template('index.html')




@app.route('/steel')
def steel():
    return render_template('steel2.html')

@app.route('/wood')
def wood():
    return render_template('wood2.html')



if __name__ == '__main__':
    app.run()