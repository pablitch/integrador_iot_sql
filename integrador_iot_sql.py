# ==========================================
# Script: integrador_iot_sql.py
# Lê mensagens do IoT Hub e insere no Azure SQL Database
# ==========================================

from azure.eventhub import EventHubConsumerClient
import pyodbc
import json
from datetime import datetime

# ============================
# CONFIGURAÇÕES DO EVENT HUB
# ============================

EVENTHUB_CONNECTION_STR = "CONEXAO-EVENT-HUB"

# ============================
# CONFIGURAÇÕES DO BANCO DE DADOS
# ============================
server = 'NOME-COMPETO-DO-SERVIDOR' # com o sufixo: .database.windows.net
database = 'robotic-mission-db-rm9999'
username = 'rm9999'
password = 'SUA-SENHA-AQUI'  # Sem @ como caracter
driver = '{ODBC Driver 18 for SQL Server}'

# Cria conexão com o Banco
try:
    conn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    print("✅ Conectado ao Banco SQL com sucesso!")
except Exception as e:
    print("❌ Erro ao conectar ao Banco SQL:", e)
    exit()

# ============================
# FUNÇÃO PARA INSERIR DADOS
# ============================
def inserir_no_banco(temperatura):
    try:
        query = "INSERT INTO sensorlogs (temperatura) VALUES (?)"
        cursor.execute(query, (temperatura,))
        conn.commit()
        print(f"💾 Dado inserido no banco: {temperatura} °C")
    except Exception as e:
        print("❌ Erro ao inserir no banco:", e)

# ============================
# CALLBACK PARA RECEBER MENSAGENS DO IOT HUB
# ============================
def on_event(partition_context, event):
    try:
        dados = json.loads(event.body_as_str())
        temperatura = dados.get("temperatura")

        if temperatura is not None:
            print(f"📡 Mensagem recebida: {temperatura} °C")
            inserir_no_banco(temperatura)
        else:
            print("⚠️ Mensagem sem campo 'temperatura':", dados)

    except Exception as e:
        print("❌ Erro ao processar mensagem:", e)

# ============================
# MAIN
# ============================
if __name__ == '__main__':
    print("🚀 Iniciando leitura do IoT Hub e gravação no SQL... (Ctrl+C para parar)\n")

    client = EventHubConsumerClient.from_connection_string(
        conn_str=EVENTHUB_CONNECTION_STR,
        consumer_group="$Default"
    )

    try:
        with client:
            client.receive(
                on_event=on_event,
                starting_position="-1"  # Lê mensagens recentes
            )
    except KeyboardInterrupt:
        print("\n🛑 Interrompido pelo usuário.")
    finally:
        cursor.close()
        conn.close()
        print("🔒 Conexão com o banco encerrada.")

