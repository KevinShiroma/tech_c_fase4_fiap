import os
import sys
import subprocess
from dotenv import load_dotenv
from azure.storage.blob import ContainerClient

from utils.audio_transcript import processar_audio_wav
from utils.video_processing import processar_video

load_dotenv()

def main(container_name, target_blob=None):
    # Condição para disparar o Streamlit (Requisito 3)
    if container_name == "dash":
        print("Iniciando o Dashboard de monitoramento (Streamlit)...")
        # Utiliza sys.executable para garantir o Python do ambiente virtual atual
        subprocess.run([sys.executable, "-m", "streamlit", "run", "utils/app.py"])
        return

    conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    container_client = ContainerClient.from_connection_string( 
        conn_str=conn_str,
        container_name=container_name
    )

    print(f"Lendo container: {container_name}")
    
    for blob in container_client.list_blobs():
        # Se um vídeo específico foi informado, ignora os outros
        if target_blob and blob.name != target_blob:
            continue
            
        blob_client = container_client.get_blob_client(blob)
        
        # Lógica para Áudio
        if container_name == "audiodata" and blob.name.endswith(".wav"):
            print(f"Enviando para audio_transcript: {blob.name}")
            processar_audio_wav(blob.name, blob_client)
            
        # Lógica para Vídeo
        elif container_name == "videodata" and blob.name.endswith(".mp4"):
            print(f"Enviando para video_processing: {blob.name}")
            processar_video(blob.name, blob_client)

        else:
            print(f"Ignorado: {blob.name}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Erro: Nome do container não fornecido.")
        print("Uso: py main.py <nome_do_container> [nome_do_video.mp4]")
        print("Exemplo de áudio/vídeo: py main.py videodata sample_video1.mp4")
        print("Exemplo para abrir o monitoramento: py main.py dashboard")
        sys.exit(1)
        
    alvo_container = sys.argv[1]
    
    # Pega o nome do arquivo se o usuário passou como terceiro argumento (índice 2)
    alvo_blob = sys.argv[2] if len(sys.argv) > 2 else None
    
    main(alvo_container, alvo_blob)