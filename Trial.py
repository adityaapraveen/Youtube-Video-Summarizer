import os
from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from flask_cors import CORS
from googletrans import Translator  # Import Translator class

import google.generativeai as genai

# Import CORS module
app = Flask(__name__)
CORS(app)

# Configure the Gemini API key
genai.configure(api_key='AIzaSyBPJoPtPj-sZTTAkmOOzdeYtuxqib3UvNg')


def fetch_and_translate_transcript(video_id, desired_language_code='en'):
    language_codes = [
        desired_language_code, 'en', 'hi', 'af', 'ak', 'sq', 'am', 'ar', 'hy', 'as', 'ay', 'az', 'bn', 'eu', 'be',
        'bho', 'bs', 'bg', 'my', 'ca', 'ceb', 'zh-Hans', 'zh-Hant', 'co', 'hr', 'cs', 'da', 'dv', 'nl', 'eo', 'et',
        'ee', 'fil', 'fi', 'fr', 'gl', 'lg', 'ka', 'de', 'el', 'gn', 'gu', 'ht', 'ha', 'haw', 'iw', 'hmn', 'hu', 'is',
        'ig', 'id', 'ga', 'it', 'ja', 'jv', 'kn', 'kk', 'km', 'rw', 'ko', 'kri', 'ku', 'ky', 'lo', 'la', 'lv', 'ln',
        'lt', 'lb', 'mk', 'mg', 'ms', 'ml', 'mt', 'mi', 'mr', 'mn', 'ne', 'nso', 'no', 'ny', 'or', 'om', 'ps', 'fa',
        'pl', 'pt', 'pa', 'qu', 'ro', 'ru', 'sm', 'sa', 'gd', 'sr', 'sn', 'sd', 'si', 'sk', 'sl', 'so', 'st', 'es',
        'su', 'sw', 'sv', 'tg', 'ta', 'tt', 'te', 'th', 'ti', 'ts', 'tr', 'tk', 'uk', 'ur', 'ug', 'uz', 'vi', 'cy',
        'fy', 'xh', 'yi', 'yo', 'zu'
    ]

    for language_code in language_codes:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language_code])
            if transcript:
                break
        except Exception as e:
            print(f"Failed to fetch transcript in '{language_code}'")

    if not transcript:
        try:
            # If transcript in desired language and other languages not available, attempt to fetch auto-generated transcript
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
        except Exception as e:
            print("Failed to fetch auto-generated transcript")
            return []

    # If auto-generated transcript is available, check if it has language code
    if transcript:
        if 'language_code' in transcript[0]:
            if transcript[0]['language_code'] != desired_language_code:
                translator = Translator()
                translated_transcript = []
                for segment in transcript:
                    text = segment['text']
                    try:
                        translated_text = translator.translate(text, dest=desired_language_code).text
                        translated_transcript.append(translated_text)
                    except IndexError:
                        print(f"Failed to translate: {text}")
                return translated_transcript
        else:
            # If language code is not available, translate the entire transcript
            translator = Translator()
            translated_transcript = []
            for segment in transcript:
                text = segment['text']
                try:
                    translated_text = translator.translate(text, dest=desired_language_code).text
                    translated_transcript.append(translated_text)
                except IndexError:
                    print(f"Failed to translate: {text}")
            return translated_transcript
    else:
        # If transcript is not available, return an empty list
        return []

        
def generate_content(prompt, video_summary):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt + " " + video_summary)
    return response.text

@app.route('/qa')
def qa_api():
    url = request.args.get('url', '')
    question = request.args.get('question', '')
    video_id = url.split('v=')[-1]  # Extract video ID from URL
    transcript = fetch_and_translate_transcript(video_id)
    summary = ' '.join(transcript)  # Convert translated transcript to summary
    response = generate_content(question, summary)
    return response, 200

@app.route('/summary')
def summary_api():
    url = request.args.get('url', '')
    video_id = url.split('v=')[-1]  # Extract video ID from URL
    transcript = fetch_and_translate_transcript(video_id)
    summary = ' '.join(transcript)  # Convert translated transcript to summary
    return summary, 200

@app.route('/conversation')
def conversation_api():
    url = request.args.get('url', '')
    prompt = request.args.get('prompt', '')
    video_id = url.split('v=')[-1]  # Extract video ID from URL
    transcript = fetch_and_translate_transcript(video_id)
    summary = ' '.join(transcript)  # Convert translated transcript to summary
    response = generate_content(prompt, summary)
    return response, 200

def get_transcript(video_id):
    transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
    transcript = ' '.join([d['text'] for d in transcript_list])
    print(transcript)
    return transcript

def get_summary(transcript):
    summary = ''
    max_length = 512  # Maximum sequence length supported by the model
    for i in range(0, len(transcript), max_length):
        segment = transcript[i:i+max_length]
        summary += segment + ' '
    return summary

if __name__ == '__main__':
    app.run()