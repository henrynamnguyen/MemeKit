from flask import Flask, jsonify, request, Response
from flask_restful import Api, Resource
import requests
from pymongo import MongoClient
import google.cloud.storage as gcs
import subprocess
import os

import imageio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from skimage.transform import resize
import warnings
warnings.filterwarnings("ignore")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= "key.json"

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")
UserDB = client["UserDB"]
User = UserDB["User"]

ALLOWED_FORMAT = ['png','jpeg','jpg']
FILE_PATH = '/MemeKit/first-order-model/'

def process_image(song_selected):
    subprocess.run('python3 demo.py --config config/vox-256.yaml --driving_video blueprint_videos/{}.mp4 --source_image temp.jpeg --checkpoint vox-cpk.pth.tar --result_video temp_files/output.mp4 --relative --adapt_scale'.format(song_selected), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell = True)
    subprocess.run('ffmpeg -i {} -i {} -c:v copy -c:a aac temp_files/output2.mp4'.format("temp_files/output.mp4","song_list/{}.mp3".format(song_selected)),shell=True)

def add_watermark(user_id):
    subprocess.run('ffmpeg -i {} -i {} -filter_complex overlay=W-w-5:H-h-5 temp_files/result.mp4'.format("temp_files/temp.jpeg", "logo.png"),shell=True)

def upload_to_storage(user_id):
    client = gcs.Client()
        
    bucket_name = "lively-iris-309008.appspot.com"
    bucket = client.get_bucket(bucket_name) #connect with "memekit" bucket
        
    blob_name = "{}/{}".format(user_id, "8")
    blob = bucket.blob(blob_name)

    with open("result.mp4","rb") as g:
            blob.upload_from_file(g,content_type="video/mp4")

def remove_temp_files():
    os.remove(FILE_PATH + 'temp_files/temp.jpeg')
    os.remove(FILE_PATH + 'temp_files/output.mp4')
    os.remove(FILE_PATH + 'temp_files/output2.mp4')
    os.remove(FILE_PATH + 'temp_files/result.mp4')

class Upload(Resource):
    def post(self):
        #get the user_id, url of users' images and song users selected
        user_data = request.get_json()
        user_id = user_data["user_id"]
        image_url = str(user_data["image_url"])
        song_selected = int(user_data["song_selected"])
        
        #read the user's image and blueprint videos
        image_data = requests.get(image_url)
        image = image_data.content
        f = open("temp.jpeg","wb")
        f.write(image)
        f.close()
        reader = imageio.get_reader('{}.mp4'.format(song_selected))
        
        #make animation and attach music
        #process_image(song_selected)
        
        #add watermarks if user is not a paying user
        #subprocess.run('ffmpeg -i {} -i {} -filter_complex overlay=W-w-5:H-h-5 result.mp4'.format("output2.mp4", "logo.png"),shell=True)
        add_watermark(user_id)

        #upload to Cloud Storage 
        upload_to_storage(user_id)
            
        #remove temp files
        remove_temp_files()


api.add_resource(Upload,"/upload")

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0')

