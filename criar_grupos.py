import requests
import json
import time
import base64
import re 
import os
from dotenv import load_dotenv

# --- CONFIGURAÇÕES Z-API ---

load_dotenv()

INSTANCIA_ID = os.getenv("INSTANCIA_ID")
INSTANCIA_TOKEN = os.getenv("INSTANCIA_TOKEN")
CLIENT_TOKEN = os.getenv("CLIENT_TOKEN")

API_URL_CRIACAO = f"https://api.z-api.io/instances/{INSTANCIA_ID}/token/{INSTANCIA_TOKEN}/create-group"
API_URL_FOTO = f"https://api.z-api.io/instances/{INSTANCIA_ID}/token/{INSTANCIA_TOKEN}/update-group-photo"
DELAY_ENTRE_GRUPOS = 5 

# --- PARTICIPANTES FIXOS ---
PARTICIPANTES_FIXOS = [
    "5527993110797", # Erick
    "5527993122277", # Financeiro
]


# ==============================================================================
# 🚨 FUNÇÃO DE CARREGAMENTO DE DADOS (DUPLA DECODIFICAÇÃO) 🚨
# ==============================================================================

def carregar_dados_grupos(caminho_arquivo):
    """Carrega dados do JSON, tratando o formato de lista de string JSON."""
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            # 1. Lê o JSON externo (lista contendo a string JSON)
            dados_externos = json.load(f)
            
            # 2. Verifica e pega a string JSON interna
            if isinstance(dados_externos, list) and len(dados_externos) == 1 and isinstance(dados_externos[0], str):
                json_string_interno = dados_externos[0]
                
                # 3. Faz o parsing da string interna para obter a lista final de dicionários
                dados_grupos_finais = json.loads(json_string_interno)
                print(f"✅ Dados carregados com sucesso de '{caminho_arquivo}'. {len(dados_grupos_finais)} grupos encontrados.")
                return dados_grupos_finais
            else:
                print(f"❌ ERRO DE FORMATO: O arquivo '{caminho_arquivo}' não está no formato esperado.")
                return []
                
    except FileNotFoundError:
        print(f"❌ ERRO: Arquivo '{caminho_arquivo}' não encontrado.")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ ERRO DE PARSING JSON: O arquivo '{caminho_arquivo}' está mal formatado. Detalhes: {e}")
        return []


# ==============================================================================
# 🚨 LEITURA E LIMPEZA DA FOTO EM BASE64 🚨
# ==============================================================================

NOME_ARQUIVO_BASE64 = "dados/icon.txt"
BASE64_FOTO_GRUPO = ""

try:
    with open(NOME_ARQUIVO_BASE64, 'r') as file:
        raw_base64 = file.read().strip()
        
        # 1. REMOVE PREFIXO, SE JÁ EXISTIR
        if "," in raw_base64:
            raw_base64 = raw_base64.split(",", 1)[-1]
        
        # 2. LIMPA RUÍDOS (mantém só caracteres válidos de Base64)
        BASE64_FOTO_GRUPO = re.sub(r'[^a-zA-Z0-9+/=]', '', raw_base64).strip()
    
    if not BASE64_FOTO_GRUPO:
        print(f"⚠️ AVISO: O arquivo '{NOME_ARQUIVO_BASE64}' está vazio ou corrompido após a limpeza.")
    else:
        # 3. RECOLOCA PREFIXO OBRIGATÓRIO (Assumindo JPEG, que é o formato de sucesso)
        BASE64_FOTO_GRUPO = f"data:image/jpeg;base64,{BASE64_FOTO_GRUPO}"

except FileNotFoundError:
    print(f"❌ ERRO: Arquivo '{NOME_ARQUIVO_BASE64}' não encontrado.")
except Exception as e:
    # Captura qualquer outro erro durante o processo de limpeza/leitura da foto
    print(f"❌ ERRO durante a leitura/limpeza do Base64: {e}")
    BASE64_FOTO_GRUPO = ""
    

# ==============================================================================
# 🚨 FUNÇÃO PRINCIPAL DE CRIAÇÃO (LÓGICA INALTERADA) 🚨
# ==============================================================================

def criar_grupos_com_participantes_fixos(lista_grupos):
    """
    Cria grupos na Z-API, adiciona participantes fixos e variáveis, 
    e envia a foto do grupo após a criação bem-sucedida.
    """
    
    if not lista_grupos:
        print("Nenhum dado de grupo para processar. Finalizando.")
        return
    
    if not BASE64_FOTO_GRUPO:
        print("Impossível prosseguir, o Base64 da foto não foi carregado.")
        # Retorna para evitar erro na linha que usa BASE64_FOTO_GRUPO
        return
    
    headers = {
        "Content-Type": "application/json",
        "Client-Token": CLIENT_TOKEN
    }
    
    print(f"Iniciando a criação de {len(lista_grupos)} grupos...")

    for i, lead_data in enumerate(lista_grupos):
        nome = lead_data.get("nome_grupo")
        numero_variavel = lead_data.get("numero_variavel")
        
        print(f"\n--- Processando Grupo {i+1}/{len(lista_grupos)}: {nome} ---")

        # 1. MONTAGEM DA LISTA FINAL DE PARTICIPANTES
        participantes_finais = list(PARTICIPANTES_FIXOS) 
        if numero_variavel:
            participantes_finais.append(numero_variavel) 
        
        print(f"   Participantes a adicionar: {participantes_finais}")

        # Monta o payload para CRIAÇÃO do grupo (Z-API)
        payload_zapi = {
            "groupName": nome, 
            "phones": participantes_finais, 
            "autoInvite": True
        }

        try:
            # 2. REQUISIÇÃO: CRIAÇÃO DO GRUPO
            response = requests.post(
                API_URL_CRIACAO, 
                headers=headers, 
                data=json.dumps(payload_zapi)
            )
            
            # 3. TRATAMENTO DE SUCESSO E ENVIO DA FOTO
            if response.status_code == 200:
                resultado = response.json()
                group_id = resultado.get('phone')
                print(f"✅ SUCESSO. Grupo criado com ID/Fone: {group_id}")
                
                # --- ENVIANDO FOTO DE PERFIL ---
                print("   Tentando adicionar foto de perfil...")
                time.sleep(2) 
                
                payload_foto = {
                    "groupId": group_id, 
                    "groupPhoto": BASE64_FOTO_GRUPO # Usa o Base64 com prefixo
                }
                
                try:
                    # REQUISIÇÃO: ENVIO DA FOTO
                    response_foto = requests.post(
                        API_URL_FOTO, 
                        headers=headers, 
                        data=json.dumps(payload_foto)
                    )
                    
                    if response_foto.status_code == 200:
                        print("   🖼️ Foto adicionada com sucesso!")
                    else:
                        print(f"   ❌ Erro ao adicionar foto ({response_foto.status_code}): {response_foto.text}")
                
                except requests.exceptions.RequestException as e:
                    print(f"   ❌ ERRO DE CONEXÃO ao enviar foto: {e}")

            # 4. TRATAMENTO DE FALHA NA CRIAÇÃO DO GRUPO
            else:
                print(f"❌ ERRO HTTP {response.status_code} ao criar '{nome}': {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"❌ ERRO DE CONEXÃO na CRIAÇÃO DO GRUPO: {e}")
        
        # 5. DELAY DE SEGURANÇA
        if i < len(lista_grupos) - 1:
            print(f"Aguardando {DELAY_ENTRE_GRUPOS}s para o próximo grupo...")
            time.sleep(DELAY_ENTRE_GRUPOS)

    print("\nProcesso de criação e configuração de grupos finalizado.")

# ==============================================================================
# 🚨 EXECUÇÃO PRINCIPAL (AGORA CARREGA DADOS DO ARQUIVO) 🚨
# ==============================================================================

if __name__ == "__main__":
    # Carrega os dados do arquivo JSON
    CAMINHO_DADOS_GRUPOS = "dados/dados_grupo.JSON"
    dados_grupos = carregar_dados_grupos(CAMINHO_DADOS_GRUPOS)
    
    # Executa a função principal com os dados carregados
    if dados_grupos:
        criar_grupos_com_participantes_fixos(dados_grupos)