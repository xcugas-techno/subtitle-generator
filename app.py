from flask import Flask, request, send_from_directory, send_file
from werkzeug.utils import secure_filename
import os
# from flask import Flask, request
import subtitle
import json

location = os.getcwd()
videos_dir = "videos"
vidoes_folder_path = os.path.join(location, videos_dir)

UPLOAD_FOLDER = vidoes_folder_path
ALLOWED_EXTENSIONS = {'mp4', 'webp'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/",methods=['POST','GET'])
def subtitledata():
    data = ""
    json_data = ""
    if(request.method == 'POST'):
        video = request.files['video']

        if video and allowed_file(video.filename):
            video_filename = secure_filename(video.filename)
            video.save(os.path.join(app.config['UPLOAD_FOLDER'], 'subtitlevideo.mp4'))
#         data = subtitle.main(video)
#     return data
      return "Hello World"
        # json_d = {"chainese_word" : chainese_word, "wav_file" : wav_file, "eng_trans" : eng_trans, "option1" : option1, "option2" : option2, "correct_answer" : correct_answer}
        # json_data=json.dumps(json_d)
        # print("json_data",json_data)
    # return json_data

if __name__ == '__main__':
    app.run(debug=True)
