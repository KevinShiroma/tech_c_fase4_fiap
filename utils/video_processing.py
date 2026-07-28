import cv2
import mediapipe as mp
import os
from tqdm import tqdm

def processar_video(blob_name, blob_client):
    if blob_client is not None:
            base_filename = os.path.basename(blob_name)
            caminho_local = f"samples/{base_filename}" # Direciona o download para a pasta existente
            
            print(f"\nBaixando {blob_name} do Azure para {caminho_local}...")
            with open(caminho_local, "wb") as f:
                f.write(blob_client.download_blob().readall())
                
            # Atualiza a variável para o OpenCV ler o arquivo do lugar certo
            blob_name = caminho_local

    # 2. Inicializar Apenas o MediaPipe
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()
    mp_drawing = mp.solutions.drawing_utils

    # 3. Configuração de Vídeo
    cap = cv2.VideoCapture(blob_name)
    if not cap.isOpened():
        print(f"Erro ao abrir o vídeo {blob_name}.")
        return

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    base_filename = os.path.basename(blob_name)

    output_path = f"output_processing_video/output_{base_filename}"
    report_path = f"reports/relatorio_{base_filename}.txt"

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    report_events = []
    falhas_count = 0
    postura_correta_anterior = True

    def check_hands_above_shoulders(landmarks):
        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
        right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]

        left_correct = left_wrist.y < left_shoulder.y
        right_correct = right_wrist.y < right_shoulder.y

        return left_correct and right_correct

    # 4. Loop de Processamento
    for frame_idx in tqdm(range(total_frames), desc=f"Processando {blob_name}"):
        ret, frame = cap.read()
        if not ret:
            break

        # Processamento MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb_frame)

        if results.pose_landmarks:
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            postura_correta = check_hands_above_shoulders(results.pose_landmarks.landmark)
            
            if not postura_correta and postura_correta_anterior:
                falhas_count += 1
                tempo_segundos = frame_idx / fps
                report_events.append(f"[FALHA] As mãos caíram abaixo da linha dos ombros no segundo {tempo_segundos:.2f} (Frame {frame_idx})")
            
            postura_correta_anterior = postura_correta
            
            status_texto = "CORRETO" if postura_correta else "INCORRETO"
            cor = (0, 255, 0) if postura_correta else (0, 0, 255)
            
            cv2.putText(frame, f'Status: {status_texto} | Falhas: {falhas_count}', (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, cor, 2, cv2.LINE_AA)

        out.write(frame)
        cv2.imshow('Analise Postural - MediaPipe', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

    # 5. Geração do Relatório
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"=== RELATÓRIO DE POSTURA: {blob_name} ===\n")
        f.write(f"Total de frames: {total_frames}\n")
        f.write(f"Total de falhas: {falhas_count}\n\n")
        if report_events:
            for event in report_events:
                f.write(event + "\n")
        else:
            f.write("Execução perfeita!\n")
            
    print(f"Concluído! Vídeo: {output_path} | Relatório: {report_path}")

# Teste local
if __name__ == "__main__":
    processar_video("samples/sample_video1.mp4", None)