import os
import ffmpeg
from pytube import YouTube
import shutil
import warnings
from time import sleep
from googletrans import Translator
import backoff
from typing import Iterator, TextIO

location = os.getcwd()
extracted_audio_dir = "extracted_audio"
extracted_folder_path = os.path.join(location, extracted_audio_dir)

isExistinput = os.path.exists(extracted_folder_path)
if(isExistinput == True):
    shutil.rmtree(extracted_folder_path)
    os.mkdir(extracted_folder_path)
elif(isExistinput == False):
    os.mkdir(extracted_folder_path)

def download_videos(video_url, video_folder_path):
    yt = YouTube(video_url)

    output = yt.streams.filter(file_extension="mp4").get_by_resolution("720p").download(video_folder_path)

    return output

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


def filename(video_path):
    return os.path.splitext(os.path.basename(video_path))[0]



def get_audio(path):
    audio_paths = {}

    print(f"Extracting audio from {filename(path)}...")
    output_path = os.path.join(extracted_folder_path, f"{filename(path)}.wav")

    ffmpeg.input(path).output(
        output_path,
        acodec="pcm_s16le", ac=1, ar="16k").run(quiet=True) #quiet=True

    audio_paths[path] = output_path

    return audio_paths

def get_subtitles(audio_paths: list, output_srt: bool, output_dir: str, transcribe: callable):
    subtitles_path = {}

    for path, audio_path in audio_paths.items():
        srt_path = os.path.join(output_dir, f"English.srt")
        
        print(
            f"Generating subtitles for {filename(path)}... This might take a while."
        )

        warnings.filterwarnings("ignore")
        result = transcribe(audio_path)
        warnings.filterwarnings("default")

        with open(srt_path, "w", encoding="utf-8") as srt:
            write_srt(result["segments"], file=srt)

        subtitles_path[path] = srt_path

    return subtitles_path[path]

class translator:
    def __init__(self):
        self.client = Translator()
        self.sleep_in_between_translations_seconds = 10
        self.source_language = "en"
        self.max_chunk_size = 4000

    def __createChunks(self, corpus):
        chunks = [corpus[i:i + self.max_chunk_size] for i in range(0, len(corpus), self.max_chunk_size)]
        return chunks

    def __sleepBetweenQuery(self):
        print('Sleeping for {}s after translation query..'.format(self.sleep_in_between_translations_seconds))
        sleep(self.sleep_in_between_translations_seconds)

    @backoff.on_exception(backoff.expo, Exception, max_tries=150)
    def Translate(self, content, dest_language_code):
        try:
            print('Attempting to translate to lang={}'.format(dest_language_code))
            if len(content) > self.max_chunk_size:
                print('Warning: Content is longer than allowed size of {}, breaking into chunks'.format(self.max_chunk_size))
                results_list = []
                concatenated_result = ""

                original_chunks = self.__createChunks(content)
                for i in original_chunks:
                    r = self.client.translate(i, dest=dest_language_code, src=self.source_language)
                    self.__sleepBetweenQuery()
                    results_list.append(r.text)

                for i in results_list:
                    concatenated_result += i

                return concatenated_result
            else:
                res = self.client.translate(content, dest=dest_language_code, src=self.source_language)
                self.__sleepBetweenQuery()
                return res.text
        except Exception as e:
            print(e)
            raise e
