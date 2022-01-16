from flask import Flask, flash, request, redirect, url_for, render_template
import urllib.request
import os
from werkzeug.utils import secure_filename

import cv2 # opencv-python==4.5.5.62
# from keras.preprocessing import image
# from keras.utils import np_utils
# from PIL import Image
import numpy as np
import requests
import json
import random

app = Flask(__name__)

 
UPLOAD_FOLDER = 'static/uploads/'
 
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/comingsoon')
def coming():
    return render_template('coming.html')
     
@app.route('/')
def home():
    return render_template('index.html')
 
@app.route('/', methods=['POST'])
def upload_image():
	if 'file' not in request.files:
		flash('<Không có tệp>')
		return redirect(request.url)
	file = request.files['file']
	if file.filename == '':
		flash('<Không có hình ảnh nào được chọn tải lên để dự đoán>')
		return redirect(request.url)
	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		flash('<Hình ảnh hiển thị thành công>')

		labels = [
			'Airplane - Máy bay',
			'Automobile - Ôtô',
			'Bird - Con Chim',
			'Cat - Con Mèo',
			'Deer - Con Nai',
			'Dog - Con Chó',
			'Frog - Con Ếch',
			'Horse - Con Ngựa',
			'Ship - Tàu/Thuyền',
			'Truck - Xe Tải'
		]

		img = cv2.imread(f'./static/uploads/{filename}')
		img = cv2.resize(img, dsize=(32, 32), interpolation=cv2.INTER_CUBIC)

		# img = Image.open(f'./static/uploads/{filename}')
		# img = img.resize((32, 32))

		# img = img.astype('float32') / 255.0
		img = np.array(img, dtype=np.float32) / 255.0
		img = img.tolist()
		url = 'https://apimodel-da2.herokuapp.com/v1/models/cnncifar10:predict'

		data = json.dumps({"signature_name": "serving_default", "instances": [img]})
		headers = {"content-type": "application/json"}
		json_response = requests.post(url, data=data, headers=headers)
		predictions = json.loads(json_response.text)['predictions']
		pred = np.argmax(predictions)
		percent = predictions[0][pred] * 100
		# per = f'{percent}%'

		return render_template('index.html', filename=filename, pre=labels[pred], per = round(percent,2))
	else:
		flash('<Các định dạng được hỗ trợ: PNG, JPG và JPEG>')
		return redirect(request.url)
 
@app.route('/display/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename='uploads/' + filename), code=301)





# picFolder = os.path.join('static', 'img-test')

# app.config['UPLOAD_FOLDER'] = picFolder


# @app.route("/test")
# def abcd():
# 	rd = random.randint(0,4000)
# 	imagesList = os.listdir('static/img-test')
# 	iL = imagesList[0:100]
# 	imagelist = ['img-test/' + image for image in iL]

# 	labels = [
# 			'Airplane - Máy bay',
# 			'Automobile - Ôtô',
# 			'Bird - Con Chim',
# 			'Cat - Con Mèo',
# 			'Deer - Con Nai',
# 			'Dog - Con Chó',
# 			'Frog - Con Ếch',
# 			'Horse - Con Ngựa',
# 			'Ship - Tàu/Thuyền',
# 			'Truck - Xe Tải'
# 		]

# 	# predList = []
# 	# perList = []
# 	# for i in iL:
# 	# 	img = cv2.imread(f'./static/img-test/{i}')
# 	# 	img = np.array(img, dtype=np.float32) / 255.0
# 	# 	img = img.tolist()
# 	# 	url = 'https://apimodel-da2.herokuapp.com/v1/models/cnncifar10:predict'

# 	# 	data = json.dumps({"signature_name": "serving_default", "instances": [img]})
# 	# 	headers = {"content-type": "application/json"}
# 	# 	json_response = requests.post(url, data=data, headers=headers)
# 	# 	predictions = json.loads(json_response.text)['predictions']

# 	# 	pred = np.argmax(predictions)
# 	# 	percent = predictions[0][pred] * 100
# 	# 	predList.append(labels[pred])
# 	# 	perList.append(percent)


# 	imgs = []
# 	for i in iL:
# 		img = cv2.imread(f'./static/img-test/{i}')
# 		imgs.append(img)
# 	imgs = np.array(imgs, dtype=np.float32) / 255.0
# 	imgs = imgs.tolist()
# 	url = 'https://apimodel-da2.herokuapp.com/v1/models/cnncifar10:predict'

# 	def make_prediction(instances):
# 		data = json.dumps({"signature_name": "serving_default", "instances": instances})
# 		headers = {"content-type": "application/json"}
# 		json_response = requests.post(url, data=data, headers=headers)
# 		predictions = json.loads(json_response.text)['predictions']
# 		return predictions

# 	for p in make_prediction(imgs):
# 		pred = np.argmax(p)
# 		print(f"dự đoán {p}:", labels[pred])

# 	# percent = predictions[0][pred] * 100
# 	# predList.append(labels[pred])
# 	# perList.append(percent)

# 	# return render_template("index_test.html", imagelist=imagelist,\
# 	# 						predList = predList, perList = perList)

# 	return render_template("index_test.html", imagelist=imagelist)



if __name__ == '__main__':
	app.run(debug=True)