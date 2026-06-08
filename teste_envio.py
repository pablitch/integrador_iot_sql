from azure.iot.device import IoTHubDeviceClient, Message
import json
import time

# Connection string do DISPOSITIVO IoT (não do IoT Hub)
DEVICE_CONNECTION_STRING = "SUA-CHAVE-CONEXAO-PRIMARIA"

def enviar_temperatura():
    client = IoTHubDeviceClient.create_from_connection_string(DEVICE_CONNECTION_STRING)
    
    try:
        for i in range(10):
            temperatura = 20 + i
            mensagem = Message(json.dumps({"temperatura": temperatura}))
            print(f"📤 Enviando: {temperatura}°C")
            client.send_message(mensagem)
            time.sleep(2)
        
        print("✅ Mensagens enviadas com sucesso!")
    finally:
        client.shutdown()

if __name__ == "__main__":
    enviar_temperatura()
