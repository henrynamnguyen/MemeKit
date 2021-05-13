from flask import Flask, jsonify, request, Response
from flask_restful import Api, Resource
import requests
from pymongo import MongoClient

import imageio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from skimage.transform import resize
import warnings
warnings.filterwarnings("ignore")

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")
UserDB = client["UserDB"]
User = UserDB["User"]

ALLOWED_FORMAT = ["png","jpeg","jpg"]

class Upload(Resource):
    def post(self):
        #get the url of users' images
        user_data = request.get_json()
        user_id = user_data["user_id"]
        image_data = str(user_data["image_url"])
        song_selected = user_data["song_selected"]
        
        image = image_data.content
        f = open("temp.jpeg","wb")
        f.write(image)
        f.close()
        
        reader = imageio.get_reader('nhatnam2.mp4')
        
        subprocess.run('python3 demo.py --config config/vox-256.yaml --driving_video nhatnam2.mp4 --source_image temp.jpg --checkpoint /content/drive/MyDrive/first-order-motion-model/vox-cpk.pth.tar --result_video output.mp4 --relative --adapt_scale', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell = True)
        
        subprocess.run('ffmpeg -i {} -i {} -c:v copy -c:a aac output2.mp4'.format("output.mp4","14.mp3".format(song_selected)),shell=True)
        
        subprocess.run('ffmpeg -i {} -i {} -filter_complex overlay=W-w-5:H-h-5 result.mp4'.format("output2.mp4", "logo.png"),shell=True)
        
        client = gcs.Client()
        
        bucket_name = "lively-iris-309008.appspot.com"
        bucket = client.get_bucket(bucket_name) #connect with "memekit" bucket
        
        blob_name = "{}/{}".format(user_id, "8")
        blob = bucket.blob(blob_name)

        with open("result.mp4","rb") as g:
            blob.upload_from_file(g,content_type="video/mp4")
            
        os.remove('/content/MemeKit/first-order-model/' + 'temp.jpg')
        os.remove('/content/MemeKit/first-order-model/' + 'output.mp4')
        os.remove('/content/MemeKit/first-order-model/' + 'output2.mp4')
        os.remove('/content/MemeKit/first-order-model/' + 'result.mp4')


api.add_resource(Upload,"/upload")

if __name__ == "__main__":
    app.run(debug=True)

