import os
import time
import azure.cognitiveservices.speech as speechsdk
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

def processar_audio_wav(blob_name, blob_client):
    # ==========================================
    # 1. Download do Arquivo (.wav ou .mp3)
    # ==========================================
    with open(blob_name, "wb") as f:
        f.write(blob_client.download_blob().readall())
    print(f"\nBaixado: {blob_name}.")
    
    # Se for mp3, apenas baixa e encerra a função
    if blob_name.endswith(".mp3"):
        return

    print("Iniciando transcrição...")

    # ==========================================
    # 2. Transcrição de Áudio (.wav) - Azure Speech
    # ==========================================
    speech_key = os.getenv("AZURE_SPEECH_KEY")
    speech_region = os.getenv("AZURE_SPEECH_REGION")

    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
    speech_config.speech_recognition_language = "en-US"

    audio_config = speechsdk.audio.AudioConfig(filename=blob_name)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    
    texto_completo = []
    transcricao_finalizada = [False]

    def ao_reconhecer(evt):
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            texto_completo.append(evt.result.text)

    def parar_transcricao(evt):
        transcricao_finalizada[0] = True

    speech_recognizer.recognized.connect(ao_reconhecer)
    speech_recognizer.session_stopped.connect(parar_transcricao)
    speech_recognizer.canceled.connect(parar_transcricao)

    speech_recognizer.start_continuous_recognition_async()

    while not transcricao_finalizada[0]:
        time.sleep(1) 

    speech_recognizer.stop_continuous_recognition_async()

    print(f"--- TEXTO DE {blob_name} ---")
    print(" ".join(texto_completo))

    if not texto_completo:
        return

    # ==========================================
    # 3. Análise de Sentimento - Azure Text Analytics
    # ==========================================
    text_endpoint = os.getenv("AZURE_TEXT_ANALYTICS_ENDPOINT")
    text_key = os.getenv("AZURE_TEXT_ANALYTICS_KEY")

    client = TextAnalyticsClient(endpoint=text_endpoint, credential=AzureKeyCredential(text_key))

    tamanho_lote = 10

    for i in range(0, len(texto_completo), tamanho_lote):
        lote = texto_completo[i : i + tamanho_lote]
        
        resultados = client.analyze_sentiment(documents=lote, language="en-US")
        
        for idx, resultado in enumerate(resultados):
            texto_original = lote[idx]
            
            if not resultado.is_error:
                is_strong_positive = (resultado.sentiment == "positive" and resultado.confidence_scores.positive > 0.80)
                is_strong_negative = (resultado.sentiment == "negative" and resultado.confidence_scores.negative > 0.80)
                
                if is_strong_positive or is_strong_negative:
                    print(f"[{resultado.sentiment.upper()}] {texto_original}")
                    print(f"Pos: {resultado.confidence_scores.positive:.2f} | "
                          f"Neu: {resultado.confidence_scores.neutral:.2f} | "
                          f"Neg: {resultado.confidence_scores.negative:.2f}\n")
            else:
                print(f"Erro na frase '{texto_original[:20]}...': {resultado.error.message}\n")