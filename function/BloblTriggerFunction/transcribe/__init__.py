import logging
import os
import tempfile
import requests
import azure.functions as func
import azure.cognitiveservices.speech as speechsdk
from azure.cosmos import CosmosClient

def main(req: func.HttpRequest) -> func.HttpResponse:
    url = req.params.get('url')
    if not url:
        return func.HttpResponse("Missing 'url' parameter", status_code=400)

    # === ENV ===
    speech_key = os.environ["SPEECH_KEY"]
    speech_region = os.environ["SPEECH_REGION"]
    cosmos_conn = os.environ["COSMOS_DB_CONN_STRING"]
    db_name = os.environ["COSMOS_DB_NAME"]
    container_name = os.environ["COSMOS_DB_CONTAINER_NAME"]
    translator_key = os.environ["TRANSLATOR_KEY"]
    translator_endpoint = os.environ["TRANSLATOR_ENDPOINT"]

    try:
        # === DOWNLOAD DO ÁUDIO ===
        audio_data = requests.get(url)
        audio_data.raise_for_status()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
            tmp_audio.write(audio_data.content)
            temp_audio_path = tmp_audio.name

        # === TRANSCRIÇÃO ===
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
        audio_config = speechsdk.audio.AudioConfig(filename=temp_audio_path)
        recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
        result = recognizer.recognize_once()
        transcription = result.text if result.reason == speechsdk.ResultReason.RecognizedSpeech else "Erro na transcrição"

        # === TRADUÇÃO ===
        headers = {
            "Ocp-Apim-Subscription-Key": translator_key,
            "Ocp-Apim-Subscription-Region": speech_region,
            "Content-type": "application/json"
        }
        params = {
            "api-version": "3.0",
            "from": "auto",
            "to": ["pt"]
        }
        body = [{"text": transcription}]
        response = requests.post(f"{translator_endpoint}/translate", params=params, headers=headers, json=body)
        response.raise_for_status()
        translation = response.json()[0]["translations"][0]["text"]

        # === SALVAR NO COSMOS ===
        client = CosmosClient.from_connection_string(cosmos_conn)
        db = client.get_database_client(db_name)
        container = db.get_container_client(container_name)
        container.upsert_item({
            "id": os.path.basename(url),
            "filename": os.path.basename(url),
            "transcription": transcription,
            "translation": translation
        })

        return func.HttpResponse(translation, status_code=200)

    except Exception as e:
        logging.error(f"Erro: {e}")
        return func.HttpResponse(f"Erro: {str(e)}", status_code=500)
