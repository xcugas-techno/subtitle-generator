import os
import ffmpeg
import whisper
import warnings
import tempfile
from typing import Iterator, TextIO

video_filename = input("Enter file path : ")

location = os.getcwd()
srt_file_dir = "srt_files"
srt_folder_path = os.path.join(location, srt_file_dir)
extracted_audio_dir = "extracted_audio"
extracted_folder_path = os.path.join(location, extracted_audio_dir)

# def str2bool(string):
#     string = string.lower()
#     str2val = {"true": True, "false": False}

#     if string in str2val:
#         return str2val[string]
#     else:
#         raise ValueError(
#             f"Expected one of {set(str2val.keys())}, got {string}")


# def format_timestamp(seconds: float, always_include_hours: bool = False):
#     assert seconds >= 0, "non-negative timestamp expected"
#     milliseconds = round(seconds * 1000.0)

#     hours = milliseconds // 3_600_000
#     milliseconds -= hours * 3_600_000

#     minutes = milliseconds // 60_000
#     milliseconds -= minutes * 60_000

#     seconds = milliseconds // 1_000
#     milliseconds -= seconds * 1_000

#     hours_marker = f"{hours}:" if always_include_hours or hours > 0 else ""
#     return f"{hours_marker}{minutes:02d}:{seconds:02d}.{milliseconds:03d}"


# def write_srt(transcript: Iterator[dict], file: TextIO):
#     for i, segment in enumerate(transcript, start=1):
#         print(
#             f"{i}\n"
#             f"{format_timestamp(segment['start'], always_include_hours=True)} --> "
#             f"{format_timestamp(segment['end'], always_include_hours=True)}\n"
#             f"{segment['text'].strip().replace('-->', '->')}\n",
#             file=file,
#             flush=True,
#         )


def filename(video_path):
    return os.path.splitext(os.path.basename(video_path))[0]

# def main(video):
#     model_name = "small"
#     output_dir = srt_folder_path
#     srt_only = True

#     if model_name.endswith(".en"):
#         warnings.warn(
#             f"{model_name} is an English-only model, forcing English detection.")
#         args["language"] = "en"

#     model = whisper.load_model(model_name)
#     audios = get_audio(video)
#     subtitles = get_subtitles(
#         audios, srt_only, output_dir, lambda audio_path: model.transcribe(audio_path, **args)
#     )

#     if srt_only:
#         return



def get_audio(path):
    global output_path
    # temp_dir = tempfile.gettempdir()

    audio_paths = {}

    # for path in paths:
    print(f"Extracting audio from {filename(path)}...")
    output_path = os.path.join(extracted_folder_path, f"{filename(path)}.wav")
    # file_name = filename(path)
    # output_path = f"{file_name}.wav"
     
    print("path : ", path)
    print("output path : ", output_path)

    # ffmpeg.input(path).output(
    #     output_path,
    #     acodec="pcm_s16le", ac=1, ar="16k"
    # ).run(quiet=True, overwrite_output=True)


    # Create a FFmpeg process to extract audio from the input video
    stream = ffmpeg.input(path)
    audio = stream.audio
    process = ffmpeg.output(audio, output_path, format='wav', acodec='pcm_s16le')

    # Run the FFmpeg process
    ffmpeg.run(process)


    audio_paths[path] = output_path

    return audio_paths

get = get_audio(video_filename)
print(get)

# def get_subtitles(audio_paths: list, output_srt: bool, output_dir: str, transcribe: callable):
#     subtitles_path = {}

#     for path, audio_path in audio_paths.items():
#         srt_path = output_dir if output_srt else tempfile.gettempdir()
#         srt_path = os.path.join(srt_path, f"{filename(path)}.srt")
        
#         print(
#             f"Generating subtitles for {filename(path)}... This might take a while."
#         )

#         warnings.filterwarnings("ignore")
#         result = transcribe(audio_path)
#         warnings.filterwarnings("default")

#         with open(srt_path, "w", encoding="utf-8") as srt:
#             write_srt(result["segments"], file=srt)

#         subtitles_path[path] = srt_path

#     return subtitles_path



# if __name__ == '__main__':
#     main(video)

