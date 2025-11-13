print("oi")
from flask import Flask, request, jsonify, render_template
from unidecode import unidecode
import pandas as pd
import requests
import json
import uuid
import re
import os

print("imports cocluidos")

# -----| CONFIG |-----
API_URL = os.environ.get("INTERNAL_API_URL", "https://chat.int.bayer.com/api/v2")
API_KEY = os.environ.get("INTERNAL_API_KEY", None)
ASSISTANT_ID = os.environ.get("ASSISTANT_ID", "db5a5273-9c09-48c9-837e-6d31e8490af9")

HEADERS = {
    "Content-Type": "application/json",
    "x-baychatgpt-accesstoken": API_KEY
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_PATH = os.path.join(BASE_DIR, "src", "data.xlsx")

app = Flask(__name__)

print("config feita")

# -----| IDENTIFICACAO DE FILTROS |-----
def definir_filtros(user_msg):
    abreviacoes = {
        "PR": "PRSC SOJA",
        "RS": "RS SOJA",
        "SC": "PRSC SOJA",
        "SP": "SAO PAULO",
    }
    
    distritos_dic = [
        "ALFENAS","ASSIS","BALSAS","CAMPO GRANDE","CAMPO MOURAO","CANOINHAS","CARAZINHO","CASCAVEL",
        "CATALAO","CHAPECO","CORNELIO PROCOP","CRUZ ALTA","CUIABA","DOURADOS","ERECHIM","FORMOSA",
        "GOIANIA","GOIATUBA","GUARAPUAVA","IBIRUBA","IJUI","IMPERATRIZ","ITAPEVA","JATAI",
        "JULIO DE CASTILHOS","LAGOA VERMELHA","LONDRINA","LUIS E MAG","MARINGA","PALMAS","PALOTINA",
        "PASSO FUNDO","PATO BRANCO","PATOS DE MINAS","PONTA GROSSA","PORTO ALEGRE","PRIMAVERA",
        "QUERENCIA","RIO DO SUL","RIO VERDE","RONDONOPOLIS","SANTA MARIA","SANTA ROSA","SANTO ANGELO",
        "SAO GABRIEL","SAO PAULO","SARANDI","SINOP","SORRISO","TOLEDO","UBERLANDIA","VILHENA"
    ]

    regionais_dict = [
        "CENTRO SOJA", "CERL SOJA", "CERO SOJA", "PRSC SOJA", "RS SOJA"
    ]

    input_usuario = user_msg.upper()
    texto = unidecode(input_usuario)

    encontrados = []

    for distrito in distritos_dic:
        padrao = r'\b' + re.escape(distrito) + r'\b'
        if re.search(padrao, texto):
            encontrados.append(distrito)

    for regional in regionais_dict:
        padrao = r'\b' + re.escape(regional) + r'\b'
        if re.search(padrao, texto):
            encontrados.append(regional)

    for sigla, nome_associado in abreviacoes.items():
        padrao_sigla = r'\b' + re.escape(sigla) + r'\b'
        if re.search(padrao_sigla, texto):
            texto += " " + nome_associado 
            encontrados.append(nome_associado)

    filtros = encontrados
    return filtros

print("funcao de filtros lida")

# -----| BUSCAR INFOS |-----
def buscar_dados(filtros):
    df = pd.read_excel('src\data.xlsx', dtype=object)
    
    target = filtros

    mask = df.applymap(lambda x: isinstance(x, str) and any(t in x for t in target))
    filtered_df = df[mask.any(axis=1)]
    
    busca_info = filtered_df.to_json(orient="records")
    return busca_info

print("funcao pandas lida")

# -----| ENVIAR MENSAGENS |-----
def enviar_mensagem(sys_msg: str, user_msg: str, conversation_id: str = None): 
    if conversation_id is None:
        conversation_id = str(uuid.uuid4())

    payload = {
        "assistant_id": ASSISTANT_ID,
        "conversation_id": conversation_id,
        "stream": False,
        "hidden": True,
        "messages": [
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": user_msg}
        ]
    }

    try:
        resp = requests.post(f"{API_URL}/chat/agent", json=payload, headers=HEADERS)
        resp.raise_for_status()
    except requests.RequestException as e:
        return None, {"error": "Falha ao conectar com a API interna", "details": str(e)}

    resp = requests.post(f"{API_URL}/chat/agent", json=payload, headers=HEADERS)
    resp.raise_for_status()
    
    try:
        data = resp.json()
    except Exception:
        data = {"raw_text": resp.text, "status_code": resp.status_code}

    assistant_msg = None
    try:
        assistant_msg = data["choices"][0]["message"]["content"]
    except Exception:
        assistant_msg = json.dumps(data, ensure_ascii=False)

    return assistant_msg, data

print("funcao de envio lida")

# -----| ROTAS FLASK |-----
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)