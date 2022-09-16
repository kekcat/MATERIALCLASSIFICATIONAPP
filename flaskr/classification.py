from keras.models import load_model
from PIL import Image, ImageOps
import numpy as np
import os


np.set_printoptions(suppress=True)

model = load_model('flaskr\Model\keras_model.h5')

with open ('flaskr\Model\labels.txt', 'r') as f:
    class_names = f.read().split('\n')


def classify():
    retdict = {}
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    
    image = Image.open('flaskr/Photos/shot.png')
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.ANTIALIAS)
    image_array = np.asarray(image)

    normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1
    data[0] = normalized_image_array

    prediction = model.predict(data)
    
    index = np.argmax(prediction)
    class_name = class_names[index]
    conf = prediction[0][index]
    print(f"Prediction: {class_name}, Confidence: {conf}")

    retdict['prediction'] = class_name
    retdict['percents'] = {}

    for index, item in enumerate(prediction[0]):
        class_name = class_names[index]
        retdict.get('percents').update({class_name: "{:.2f}".format(float(item * 100)).split('.')[0]})
    print(retdict)

    os.remove('flaskr/Photos/shot.png')

    return retdict





