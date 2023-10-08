import os
import json
import logging
from uuid import uuid4
from google.cloud import texttospeech, storage
from http.server import HTTPServer, BaseHTTPRequestHandler

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize Google Cloud clients
text_to_speech_client = texttospeech.TextToSpeechClient()
gcs_client = storage.Client()

# Define the HTTP request handler
class RequestHandler(BaseHTTPRequestHandler):
    def _send_response(self, status, content_type, response_body):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.end_headers()
        self.wfile.write(response_body)

    def do_GET(self):
        if self.path == "/":
        #   self._send_response(200, "text/plain", b"ok")
        #elif self.path == "/":
            self._serve_index_html()
        else:
            self._send_response(404, "text/plain", b"Not Found")

    def do_POST(self):
        if self.path == "/synthesize":
            self._synthesize_text()
        else:
            self._send_response(404, "text/plain", b"Not Found")

    def _serve_index_html(self):
        # Read and serve the index.html file
        try:
            with open("index.html", "rb") as file:
                self._send_response(200, "text/html", file.read())
        except FileNotFoundError:
            self._send_response(404, "text/plain", b"index.html not found")

    def _synthesize_text(self):
        content_length = int(self.headers['Content-Length'])
        request_body = self.rfile.read(content_length)
        request_json = json.loads(request_body.decode("utf-8"))

        text = request_json.get("text")
        if not text:
            self._send_response(400, "text/plain", b"Missing 'text' parameter")
            return

        tts_request = self._create_tts_request(text)
        response = text_to_speech_client.synthesize_speech(request=tts_request)

        if response.audio_content:
            filename = self._generate_filename()
            self._upload_audio_to_gcs(response.audio_content, filename)
            url = self._make_blob_publicly_accessible(filename)

            # url = self._get_public_url(filename)
            response_json = json.dumps({"url": url}).encode("utf-8")
            self._send_response(200, "application/json", response_json)
        else:
            self._send_response(500, "text/plain", b"Text-to-speech response is empty")

    def _create_tts_request(self, text):
        tts_request = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="id-ID",  # Change to your desired language code
            name="id-ID-Wavenet-C",
            ssml_gender=texttospeech.SsmlVoiceGender.MALE,
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        return texttospeech.SynthesizeSpeechRequest(
            input=tts_request, voice=voice, audio_config=audio_config
        )

    def _generate_filename(self):
        return f"{uuid4()}.mp3"

    def _upload_audio_to_gcs(self, audio_content, filename):
        bucket_name = "bucket-dafa"  # Change to your bucket name
        bucket = gcs_client.bucket(bucket_name)
        blob = bucket.blob(filename)
        blob.upload_from_string(audio_content, content_type="audio/mpeg")

    def _make_blob_publicly_accessible(self, filename):
        bucket_name = "bucket-dafa"  # Change to your bucket name
        bucket = gcs_client.bucket(bucket_name)
        blob = bucket.blob(filename)
        #blob.acl.all().grant_read()
        blob.make_public()
        public_url = blob.public_url

        return public_url

#    def _get_public_url(self, filename):
#        bucket_name = "bucket-dafa"  # Change to your bucket name
#        blob = bucket.blob(filename)
#        public_url = blob.public_url
#        return f"https://storage.googleapis.com/{bucket_name}/{filename}"


if __name__ == "__main__":
    server_address = ("", 8080)
    httpd = HTTPServer(server_address, RequestHandler)
    logging.info("Server started on port 8080.")
    httpd.serve_forever()

