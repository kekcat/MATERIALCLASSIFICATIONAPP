from flask import Flask, render_template, Response, request, redirect, flash, url_for
from classification import classify
from werkzeug.utils import secure_filename
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
global imagVar
imageVar = 0
global imgLinks
global fileTypes
FileTypes = {'png', 'jpg', 'jpeg'}
p = 'flaskr/Photos/shot.png'
ddata = {'prediction': 'Steel', 'percents': {'Wood': '0', 'Steel': '0', 'Concrete': '0', 'Obsidian': '0', 'Coal': '0', 'Conglomerate': '0', 'Copper': '0', 'Bismuth': '0', 'Gold': '0', 'Granite': '0'}}


try:
    os.mkdir('./Photos')
except OSError as error:
    pass


app = Flask(__name__, template_folder='./templates')
app.config['UPLOAD_FOLDER'] = 'flaskr\Photos'
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
    global imageVar

    if request.method == 'POST':
        if request.form.get('mat'):
            matPage = request.form.get('mat')

            page = f"{globaltempath}{matPage}/{matPage.lower()}.html"
            ddata['prediction'] = matPage
            ddata['percents'][matPage] = '100'
            return render_template(page, data=ddata)
        
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


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in FileTypes

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':

        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print("File Recieved")

            typedata = classify(image=filename)

            pageDec = typedata['prediction'].lower()
            pageDec = f"{globaltempath}{typedata['prediction'].lower()}/{pageDec}.html"
            print(pageDec)
            return render_template(pageDec, data=typedata)
        
    return render_template("filetype.html")


@app.route('/steel')
def steel():
    return render_template('flaskr\templates\materialPages\steel\steel2.html')

@app.route('/wood')
def wood():
    return render_template('flaskr\templates\materialPages\wood\wood2.html')

@app.route('/test')
def test():
    return render_template('flaskr\templates\materialPages\steel\steel copy.html')

if __name__ == '__main__':  
    app.config['UPLOAD_FOLDER'] = 'flaskr/Photos'
    app.run()