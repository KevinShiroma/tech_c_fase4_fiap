import streamlit as st
import pandas as pd
import time
import os
import subprocess

st.set_page_config(page_title="Monitoramento UTI", layout="wide")

st.title("Monitoramento Contínuo de Sinais Vitais")
st.write("Dashboard para análise em tempo real e detecção de anomalias.")

INPUT_DIR = './input_data'
os.makedirs(INPUT_DIR, exist_ok=True)

if st.button("Ligar Monitoramento Automático"):
    # Dispara o simulador em segundo plano
    subprocess.Popen(["python", "utils/simulate_streaming_data.py"])
    
    st.success(f"Simulador iniciado! Aguardando arquivos na pasta '{INPUT_DIR}'...")
    
    # Placeholders para separar as métricas da tabela
    dashboard_placeholder = st.empty()
    st.divider()
    history_placeholder = st.empty()
    
    processed_files = set()
    historico = []
    
    while True:
        arquivos = [f for f in os.listdir(INPUT_DIR) if f.endswith('.csv')]
        
        for arquivo in arquivos:
            if arquivo not in processed_files:
                file_path = os.path.join(INPUT_DIR, arquivo)
                
                try:
                    df = pd.read_csv(file_path)
                    
                    for index, row in df.iterrows():
                        subject_id = row.get('Subject ID', 1)
                        hr = row.get('Heart rate reading 1', 80)
                        o2 = row.get('Oxygen saturation reading 1', 98)
                        temp = row.get('Temperature reading 1', 36.5)
                        
                        is_anomaly = False
                        motivos = []
                        
                        if o2 < 95 or o2 > 100:
                            is_anomaly = True
                            motivos.append(f"O2 anormal")
                        if hr > 100:
                            is_anomaly = True
                            motivos.append(f"Taquicardia")
                        if temp < 35 or temp > 37.8:
                            is_anomaly = True
                            motivos.append(f"Temp crítica")
                            
                        status = "🚨 " + ", ".join(motivos) if is_anomaly else "✅ Normal"
                        
                        # Adiciona a leitura ao histórico
                        historico.append({
                            "Paciente": subject_id,
                            "Batimentos": hr,
                            "O2": o2,
                            "Temp": temp,
                            "Status": status
                        })
                        
                        # Atualiza as métricas principais
                        with dashboard_placeholder.container():
                            st.subheader(f"Monitorando Paciente: {subject_id}")
                            col1, col2, col3 = st.columns(3)
                            col1.metric("Frequência Cardíaca", f"{hr} bpm")
                            col2.metric("Saturação (O2)", f"{o2} %")
                            col3.metric("Temperatura", f"{temp} °C")
                            
                        # Atualiza a tabela de histórico (mostrando os 15 últimos registros)
                        with history_placeholder.container():
                            st.markdown("### Histórico de Leituras")
                            df_historico = pd.DataFrame(historico).tail(15)
                            st.dataframe(df_historico, use_container_width=True, hide_index=True)
                        
                        if is_anomaly:
                            st.toast(f"Paciente {subject_id} em risco!", icon='🚨')
                            time.sleep(2.0)
                        else:
                            time.sleep(0.5)
                            
                    processed_files.add(arquivo)
                except Exception as e:
                    pass
                    
        time.sleep(2)