# ==========================================
# Script: integrador_iot_sql.py
# Lê mensagens do IoT Hub e insere no Azure SQL Database
# ==========================================

from azure.eventhub import EventHubConsumerClient
import pyodbc
import json

# ============================
# CONFIGURAÇÕES DO EVENT HUB
# ============================

EVENTHUB_CONNECTION_STR = "SUA_CONNECTION_STRING_DO_EVENT_HUB"

# ============================
# CONFIGURAÇÕES DO BANCO DE DADOS
# ============================
server = 'tcp:sr-robotic-mission-db-rm9999.database.windows.net,1433'
database = 'robotic-mission-db-rm96322'
username = 'robotic'
password = 'SUA_SENHA_DO_BANCO'
driver = '{ODBC Driver 18 for SQL Server}'

# Cria conexão com o Banco
try:
    conn_str = (
        f'DRIVER={driver};'
        f'SERVER={server};'
        f'DATABASE={database};'
        f'UID={username};'
        f'PWD={password};'
        'Encrypt=yes;'
        'TrustServerCertificate=no;'
        'Connection Timeout=30;'
    )

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
        mensagem = event.body_as_str()
        print("📩 Mensagem recebida bruta:", mensagem)

        dados = json.loads(mensagem)

        # Aceita tanto o campo em português quanto em inglês
        temperatura = dados.get("temperatura") or dados.get("temperature")

        if temperatura is not None:
            print(f"📡 Temperatura recebida: {temperatura} °C")
            inserir_no_banco(temperatura)
        else:
            print("⚠️ Mensagem sem campo de temperatura:", dados)

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
                starting_position="@latest"
            )

    except KeyboardInterrupt:
        print("\n🛑 Interrompido pelo usuário.")

    finally:
        cursor.close()
        conn.close()
        print("🔒 Conexão com o banco encerrada.")
