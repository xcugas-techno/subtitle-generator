# import os
# import nltk
# from nltk.corpus import wordnet as wn
# from gtts import gTTS
# import translators as ts

# location = os.getcwd()
# wav_file_dir = "wav_files"
# wav_folder_path = os.path.join(location, wav_file_dir)


# def tts(chainese_word):
#     # Language in which you want to convert the text
#     language = 'zh' 
#     # Passing the text and language to the engine
#     tts = gTTS(text=chainese_word, lang=language, slow=False)
#     # Saving the converted audio to a file
#     wav_file = tts.save(os.path.join(wav_folder_path, 'word_review2.wav'))
#     wav_file_name = os.path.join(wav_folder_path, 'word_review2.wav')
#     return wav_file_name
    
# def translator(chainese_word):
#     # eng_trans = ts.translate_text(word, translator='baidu', to_language='en') #ZN-CN
#     eng_trans = ts.translate_text(chainese_word, translator='google', from_language='zh-TW', to_language='en-US') #ZN-CN
#     return eng_trans
    

# def synonym(eng_trans):

#     synonyms = []

#     for syn in wn.synsets(eng_trans):
#         for lemma in syn.lemmas():
#             synonyms.append(lemma.name())

   
#     syno=[]
#     [syno.append(x) for x in synonyms if x not in syno]
    
#     option1 = syno[1]

#     return option1

      
# def antonym(eng_trans):

#     antonyms = []

#     for syn in wn.synsets(eng_trans):
#         for lemma in syn.lemmas():
#             if lemma.antonyms():
#                 antonyms.append(lemma.antonyms()[0].name())
    
#     anto=[]
#     [anto.append(x) for x in antonyms if x not in anto]
    
#     option2 = anto[0]

#     return option2
    

# def word_quiz(chainese_word, eng_trans, option1, option2):
#     QUESTIONS = {
#         chainese_word: [
#             eng_trans, option1, option2
#         ]
#     }

#     for question, alternatives in QUESTIONS.items():
#         correct_answer = alternatives[0]
#         sorted_alternatives = sorted(alternatives)
#         # for label, alternative in enumerate(sorted_alternatives):
#             # print(f"  {label}) {alternative}")
#     return correct_answer




import os
import ffmpeg
import whisper
import argparse
import warnings
import tempfile

location = os.getcwd()
wav_file_dir = "srt_files/"
wav_folder_path = os.path.join(location, wav_file_dir)

def main(video):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("video", video = video, nargs="+", type=str,
                        help="paths to video files to transcribe")
    parser.add_argument("--model", default="small",
                        choices=whisper.available_models(), help="name of the Whisper model to use")
    parser.add_argument("--output_dir", "-o",type=str,
                        default=wav_folder_path, help="directory to save the outputs")
    parser.add_argument("--srt_only", srt_only=srt_only, type=str2bool, default=True,  
                        help="only generate the .srt file and not create overlayed video")
    parser.add_argument("--verbose", type=str2bool, default=False,
                        help="whether to print out the progress and debug messages")

    parser.add_argument("--task", type=str, default="transcribe", choices=[
                        "transcribe", "translate"], help="whether to perform X->X speech recognition ('transcribe') or X->English translation ('translate')")

    args = parser.parse_args().__dict__
    model_name: str = args.pop("model")
    output_dir: str = args.pop("output_dir")
    output_srt: bool = args.pop("output_srt")
    srt_only: bool = args.pop("srt_only")
    os.makedirs(output_dir, exist_ok=True)

    if model_name.endswith(".en"):
        warnings.warn(
            f"{model_name} is an English-only model, forcing English detection.")
        args["language"] = "en"

    model = whisper.load_model(model_name)
    audios = get_audio(args.pop("video"))
    subtitles = get_subtitles(
        audios, output_srt or srt_only, output_dir, lambda audio_path: model.transcribe(audio_path, **args)
    )

    if srt_only:
        return

    for path, srt_path in subtitles.items():
        out_path = os.path.join(output_dir, f"{filename(path)}.mp4")

        print(f"Adding subtitles to {filename(path)}...")

        video = ffmpeg.input(path)
        audio = video.audio

        ffmpeg.concat(
            video.filter('subtitles', srt_path, force_style="OutlineColour=&H40000000,BorderStyle=3"), audio, v=1, a=1
        ).output(out_path).run(quiet=True, overwrite_output=True)

        print(f"Saved subtitled video to {os.path.abspath(out_path)}.")


def get_audio(paths):
    temp_dir = tempfile.gettempdir()

    audio_paths = {}

    for path in paths:
        print(f"Extracting audio from {filename(path)}...")
        output_path = os.path.join(temp_dir, f"{filename(path)}.wav")

        ffmpeg.input(path).output(
            output_path,
            acodec="pcm_s16le", ac=1, ar="16k"
        ).run(quiet=True, overwrite_output=True)

        audio_paths[path] = output_path

    return audio_paths


def get_subtitles(audio_paths: list, output_srt: bool, output_dir: str, transcribe: callable):
    subtitles_path = {}

    for path, audio_path in audio_paths.items():
        srt_path = output_dir if output_srt else tempfile.gettempdir()
        srt_path = os.path.join(srt_path, f"{filename(path)}.srt")
        
        print(
            f"Generating subtitles for {filename(path)}... This might take a while."
        )

        warnings.filterwarnings("ignore")
        result = transcribe(audio_path)
        warnings.filterwarnings("default")

        with open(srt_path, "w", encoding="utf-8") as srt:
            write_srt(result["segments"], file=srt)

        subtitles_path[path] = srt_path

    return subtitles_path


import os
from typing import Iterator, TextIO


def str2bool(string):
    string = string.lower()
    str2val = {"true": True, "false": False}

    if string in str2val:
        return str2val[string]
    else:
        raise ValueError(
            f"Expected one of {set(str2val.keys())}, got {string}")


def format_timestamp(seconds: float, always_include_hours: bool = False):
    assert seconds >= 0, "non-negative timestamp expected"
    milliseconds = round(seconds * 1000.0)

    hours = milliseconds // 3_600_000
    milliseconds -= hours * 3_600_000

    minutes = milliseconds // 60_000
    milliseconds -= minutes * 60_000

    seconds = milliseconds // 1_000
    milliseconds -= seconds * 1_000

    hours_marker = f"{hours}:" if always_include_hours or hours > 0 else ""
    return f"{hours_marker}{minutes:02d}:{seconds:02d}.{milliseconds:03d}"


def write_srt(transcript: Iterator[dict], file: TextIO):
    for i, segment in enumerate(transcript, start=1):
        print(
            f"{i}\n"
            f"{format_timestamp(segment['start'], always_include_hours=True)} --> "
            f"{format_timestamp(segment['end'], always_include_hours=True)}\n"
            f"{segment['text'].strip().replace('-->', '->')}\n",
            file=file,
            flush=True,
        )


def filename(path):
    return os.path.splitext(os.path.basename(path))[0]


if __name__ == '__main__':
    main(video)