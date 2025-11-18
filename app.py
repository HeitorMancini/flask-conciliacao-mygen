from flask import Flask, request, jsonify, render_template
from unidecode import unidecode
import pandas as pd
import requests
import json
import uuid
import re
import os

# ----| CONFIG |----
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_PATH = os.path.join(BASE_DIR, "src", "data.xlsx")

app = Flask(__name__)

# -----| IDENTIFICACAO DE FILTROS |-----
def definir_filtros(user_msg, conversation_id: str = None):
    if conversation_id is None:
        conversation_id = str(uuid.uuid4())
    
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
    return filtros, conversation_id

# -----| BUSCAR INFOS |-----
def buscar_dados(filtros):
    df = pd.read_excel('src\data.xlsx', dtype=object)
    
    target = filtros

    mask = df.applymap(lambda x: isinstance(x, str) and any(t in x for t in target))
    filtered_df = df[mask.any(axis=1)]
    
    busca_info = filtered_df.to_json(orient="records")
    return busca_info

# -----| ROTAS FLASK |-----
@app.route("/")
def index():

    # -----| VARIAVEIS FRONT - AQUI|-----
    

    HEADERS = {
        "Content-Type": "application/json",
        "x-baychatgpt-accesstoken": API_KEY
    }
    return render_template("index.html",
                           api_url=API_URL,
                           api_key=API_KEY,
                           assistant_id=ASSISTANT_ID,
                           headers=HEADERS)

@app.route("/api/chat", methods=["POST"])

def chat():
    user_msg = request.form.get('message', '').strip()

    if not user_msg:
        return jsonify({'error': 'A mensagem não pode estar vazia'}), 400
    
    try:
        filtros, conversation_id = definir_filtros(user_msg)
        sys_msg = buscar_dados(filtros)

        return jsonify({
            'conversation_id': conversation_id,
            'context': sys_msg,
            'user': user_msg
        })
    except Exception as e:
        return jsonify({'error': f'Erro no processamento: {str(e)}'}), 500
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)