import os
import time
import pandas as pd
from sklearn.ensemble import IsolationForest

INPUT_DIR = './input_data'
os.makedirs(INPUT_DIR, exist_ok=True)

print(f"Monitorando a pasta '{INPUT_DIR}' por novos CSVs...")
processed_files = set()

while True:
    try:
        files = os.listdir(INPUT_DIR)
        for file in files:
            if file.endswith('.csv') and file not in processed_files:
                file_path = os.path.join(INPUT_DIR, file)
                print(f"\n[INFO] Novo arquivo detectado: {file}")
                
                df = pd.read_csv(file_path)
                
                # Simula o processamento linha a linha (tempo real)
                for index, row in df.iterrows():
                    subject_id = row.get('Subject ID', 1)
                    hr = row.get('Heart rate reading 1', 80)
                    o2 = row.get('Oxygen saturation reading 1', 98)
                    temp = row.get('Temperature reading 1', 36.5)
                    
                    # Lógica de detecção de anomalias (Requisito 3)
                    is_anomaly = False
                    motivos = []
                    
                    if o2 < 95 or o2 > 100:
                        is_anomaly = True
                        motivos.append(f"Saturação anormal ({o2}%)")
                    if hr > 100:
                        is_anomaly = True
                        motivos.append(f"Taquicardia ({hr} bpm)")
                    if temp < 35 or temp > 37.8:
                        is_anomaly = True
                        motivos.append(f"Temperatura crítica ({temp}°C)")
                        
                    if is_anomaly:
                        print(f"  -> [ALERTA MÉDICO] Paciente {subject_id}: {', '.join(motivos)}")
                    else:
                        print(f"  -> [Normal] Paciente {subject_id} - HR: {hr} | O2: {o2}")
                        
                    time.sleep(0.5) # Simula o intervalo de leitura do monitor
                
                processed_files.add(file)
                print(f"[SUCESSO] Arquivo {file} processado com sucesso!\n")
                
    except Exception as e:
        print(f"Erro: {e}")
        
    time.sleep(3)