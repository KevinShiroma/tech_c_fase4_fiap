import os
import shutil
import time

# Configuração de diretórios
PASTA_ORIGEM = './raw_data'   # Coloque todos os seus data_1.csv, data_2.csv aqui
PASTA_DESTINO = './input_data' # O Streamlit está escutando esta pasta

# Cria as pastas caso não existam
os.makedirs(PASTA_ORIGEM, exist_ok=True)
os.makedirs(PASTA_DESTINO, exist_ok=True)

# Lista e ordena os arquivos para garantir a sequência correta
arquivos = sorted([f for f in os.listdir(PASTA_ORIGEM) if f.endswith('.csv')])

if not arquivos:
    print(f"Nenhum arquivo .csv encontrado na pasta {PASTA_ORIGEM}.")
else:
    print(f"Iniciando envio de {len(arquivos)} arquivos...")

    for arquivo in arquivos:
        origem = os.path.join(PASTA_ORIGEM, arquivo)
        destino = os.path.join(PASTA_DESTINO, arquivo)
        
        # Copia o arquivo para a pasta destino
        shutil.copy(origem, destino)
        print(f"[+] Arquivo {arquivo} enviado com sucesso!")
        
        # Define o intervalo entre o envio de cada arquivo (ex: 15 segundos)
        time.sleep(3)

    print("Simulação finalizada.")