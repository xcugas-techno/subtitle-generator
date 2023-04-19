from flask import Flask, request,send_from_directory
import os
import json
import whisper
import shutil
import subtitle
import pysrt
import warnings

location = os.getcwd()
video_dir = "video"
video_folder_path = os.path.join(location, video_dir)

srt_file_dir = "srt_files"
srt_folder_path = os.path.join(location, srt_file_dir)

VIDEO_UPLOAD_FOLDER = video_folder_path
ALLOWED_EXTENSIONS = {'mp4'}

app = Flask(__name__)
app.config['VIDEO_UPLOAD_FOLDER'] = VIDEO_UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Subtitle Generator
@app.route("/subtitle_gen",methods=['POST','GET'])
def subtitle_gen():
  filename = ""
  data = ""
  json_data = ""
  if(request.method == 'POST'):
    try: 
      isExistinput = os.path.exists(video_folder_path)
      if(isExistinput == True):
        shutil.rmtree(video_folder_path)
        os.mkdir(video_folder_path)
      elif(isExistinput == False):
        os.mkdir(video_folder_path)

      video = request.files['video']

      if video and allowed_file(video.filename):
        filename = os.path.join(app.config['VIDEO_UPLOAD_FOLDER'], "uploaded_video.mp4")
        video.save(filename)
    
      isExistinput = os.path.exists(srt_folder_path)
      if(isExistinput == True):
          shutil.rmtree(srt_folder_path)
          os.mkdir(srt_folder_path)
      elif(isExistinput == False):
          os.mkdir(srt_folder_path)

      model_name = "small"
      output_dir = srt_folder_path
      srt_only = True

      if model_name.endswith(".en"):
        warnings.warn(
            f"{model_name} is an English-only model, forcing English detection.")
        args["language"] = "en"

      model = whisper.load_model(model_name)
      audios = subtitle.get_audio(filename)
      english_srt_file = subtitle.get_subtitles(
        audios, srt_only, output_dir, lambda audio_path: model.transcribe(audio_path, fp16=False)
      )

      json_d = {"status":"success", "video" : filename, "english_srt_file" : english_srt_file}
      json_data=json.dumps(json_d)
      print("json_data",json_data)
      return json_data
    except Exception as e:
      json_d = {"status":"failed","error":str(e)}
      json_data=json.dumps(json_d)
      return json_data

# Subtitle Generator using video url
@app.route("/videourl_subtitle",methods=['POST','GET'])
def url_subtitle():
  filename = ""
  data = ""
  json_data = ""
  if(request.method == 'POST'):
    try: 
      isExistinput = os.path.exists(video_folder_path)
      if(isExistinput == True):
        shutil.rmtree(video_folder_path)
        os.mkdir(video_folder_path)
      elif(isExistinput == False):
        os.mkdir(video_folder_path)

      video_url = request.form['video_url']
      download_videos = subtitle.download_videos(video_url, video_folder_path)
      print(download_videos)
    
      isExistinput = os.path.exists(srt_folder_path)
      if(isExistinput == True):
          shutil.rmtree(srt_folder_path)
          os.mkdir(srt_folder_path)
      elif(isExistinput == False):
          os.mkdir(srt_folder_path)

      model_name = "small"
      output_dir = srt_folder_path
      srt_only = True

      if model_name.endswith(".en"):
        warnings.warn(
            f"{model_name} is an English-only model, forcing English detection.")
        args["language"] = "en"

      model = whisper.load_model(model_name)
      audios = subtitle.get_audio(download_videos)
      english_srt_file = subtitle.get_subtitles(
        audios, srt_only, output_dir, lambda audio_path: model.transcribe(audio_path, fp16=False)
      )

      json_d = {"status":"success", "video" : filename, "english_srt_file" : english_srt_file}
      json_data=json.dumps(json_d)
      print("json_data",json_data)
      return json_data
    except Exception as e:
      json_d = {"status":"failed","error":str(e)}
      json_data=json.dumps(json_d)
      return json_data

@app.route("/chainesesrt_gen",methods=['POST','GET'])
def chainese():
  try:
    english_srt_file = '/home/englishtubesubtitle/Desktop/subtitle-gen/srt_files/English.srt'
    
    subs = pysrt.open(english_srt_file)

    # Initialize the translator
    translator_object = subtitle.translator()
    dest_language_code = 'zh-CN'

    # Translate each subtitle and replace the text
    for sub in subs:
        sub.text = translator_object.Translate(sub.text,dest_language_code)

    # Save the translated SRT file
    chainese_srt_file = os.path.join(srt_folder_path + "/" + "Chainese.srt")
    subs.save(chainese_srt_file, encoding='utf-8')

    print(chainese_srt_file)
    json_d = {"status":"success", "chainese_srt_file" : chainese_srt_file}
    json_data=json.dumps(json_d)
    print("json_data",json_data)
    return json_data
  except Exception as e:
    json_d = {"status":"failed","error":str(e)}
    json_data=json.dumps(json_d)
    return json_data

@app.route("/japanesesrt_gen",methods=['POST','GET'])
def japanese():
  try:
    english_srt_file = '/home/englishtubesubtitle/Desktop/subtitle-gen/srt_files/English.srt'
    
    subs = pysrt.open(english_srt_file)

    # Initialize the translator
    translator_object = subtitle.translator()
    dest_language_code = 'ja'

    # Translate each subtitle and replace the text
    for sub in subs:
      sub.text = translator_object.Translate(sub.text,dest_language_code)

    # Save the translated SRT file
    japanese_srt_file = os.path.join(srt_folder_path + "/" + "Japanese.srt")
    subs.save(japanese_srt_file, encoding='utf-8')

    json_d = {"status":"success", "japanese_srt_file" : japanese_srt_file}
    json_data=json.dumps(json_d)
    print("json_data",json_data)
    return json_data
  except Exception as e:
    json_d = {"status":"failed","error":str(e)}
    json_data=json.dumps(json_d)
    return json_data

@app.route("/koreansrt_gen",methods=['POST','GET'])
def korean():
  try:
    english_srt_file = '/home/englishtubesubtitle/Desktop/subtitle-gen/srt_files/English.srt'
    
    subs = pysrt.open(english_srt_file)

    # Initialize the translator
    translator_object = subtitle.translator()
    dest_language_code = 'ko'

    # Translate each subtitle and replace the text
    for sub in subs:
        sub.text = translator_object.Translate(sub.text,dest_language_code)

    # Save the translated SRT file
    korean_srt_file = os.path.join(srt_folder_path + "/" + "Korean.srt")
    subs.save(korean_srt_file, encoding='utf-8')

    json_d = {"status":"success", "korean_srt_file" : korean_srt_file}
    json_data=json.dumps(json_d)
    print("json_data",json_data)
    return json_data
  except Exception as e:
    json_d = {"status":"failed","error":str(e)}
    json_data=json.dumps(json_d)
    return json_data

@app.route('/download/english/srt')
def downloadenglishsrt():
  filename = "English.srt"
  path = os.path.join(srt_folder_path, filename)
  if os.path.isfile(path):
      return send_from_directory(srt_folder_path, filename)
  return "No file found"

@app.route('/download/chainese/srt')
def downloadchainesesrt():
  filename = "Chainese.srt"
  path = os.path.join(srt_folder_path, filename)
  if os.path.isfile(path):
      return send_from_directory(srt_folder_path, filename)
  return "No file found"

@app.route('/download/japanese/srt')
def downloadjapanesesrt():
  filename = "Japanese.srt"
  path = os.path.join(srt_folder_path, filename)
  if os.path.isfile(path):
      return send_from_directory(srt_folder_path, filename)
  return "No file found"

@app.route('/download/korean/srt')
def downloadkoreansrt():
  filename = "Korean.srt"
  path = os.path.join(srt_folder_path, filename)
  if os.path.isfile(path):
      return send_from_directory(srt_folder_path, filename)
  return "No file found"


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080, debug=True)
