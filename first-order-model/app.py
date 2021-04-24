from flask import Flask, jsonify, request, Response
from flask_restful import Api, Resource
import requests
from pymongo import MongoClient

import imageio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from skimage.transform import resize
from IPython.display import HTML
import warnings
warnings.filterwarnings("ignore")
from demo import load_checkpoints, make_animation
from skimage import img_as_ubyte

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
        image_url = user_data["image_url"]
        
        #load images and the blueprint videos
        source_image = imageio.imread(image_url)
        reader = imageio.get_reader("https://storage.googleapis.com/memekit-blueprint-videos/nhatnam2.mp4")
        source_image = resize(source_image, (256, 256))[..., :3]

        fps = reader.get_meta_data()['fps']
        driving_video = []
        try:
            for im in reader:
                driving_video.append(im)
        except RuntimeError:
            pass
        reader.close()
        driving_video = [resize(frame, (256, 256))[..., :3] for frame in driving_video]
 
        #load checkpoints
        generator, kp_detector = load_checkpoints(config_path='config/vox-256.yaml', 
                                checkpoint_path='https://storage.googleapis.com/memekit-checkpoint/vox-cpk.pth.tar')
        
        #perform image processing 
        predictions = make_animation(source_image, driving_video, generator, kp_detector, relative=True)
        with open("temp.mp4") as f:
            f.write(predictions)
            return Response(predictions, mimetype="video/mp4")

api.add_resource(Upload,"/Upload")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

