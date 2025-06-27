
import os
import re
from dotenv import load_dotenv
from flask import Flask, request, render_template
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai


load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-pro")


app = Flask(__name__)


def get_video_id(url):
   match = re.search(r"v=([^&]+)", url)
   return match.group(1) if match else None


def get_transcript(video_url):
   video_id = get_video_id(video_url)
   transcript = YouTubeTranscriptApi.get_transcript(video_id)
   return " ".join([t["text"] for t in transcript])


def summarize_text(text):
   if len(text.split()) > 3000:
       text = text[:15000]
   response = model.generate_content(f"Summarize this YouTube vide transcript:\n\n{text}")
   return response.text


@app.route("/", methods=["GET", "POST"])
def index():
   summary = None
   if request.method == "POST":
       url = request.form["url"]
       try:
           transcript = get_transcript(url)
           summary = summarize_text(transcript)
       except Exception as e:
           summary = f"Error: {str(e)}"
   return render_template("index.html", summary=summary)


if __name__ == "__main__":
   app.run(debug=True)