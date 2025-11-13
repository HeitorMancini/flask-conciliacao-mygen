import requests
import json
import uuid
import re
from unidecode import unidecode
import pandas as pd

API_URL = 'https://chat.int.bayer.com/api/v2'
API_KEY = "mga-797f7606c1a9c4f7668a17dd7189f0f9873b31fd"
ASSISTANT_ID = "db5a5273-9c09-48c9-837e-6d31e8490af9"

HEADERS = {
    "Content-Type": "application/json",
    "x-baychatgpt-accesstoken": API_KEY
}

# FUNÇÃO PRINCIPAL DO MYGENAI
def enviar_mensagem(sys_msg: str, user_msg: str, conversation_id: str = None): 
    if conversation_id is None:
        conversation_id = str(uuid.uuid4())
    
    # print(conversation_id)

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

    resp = requests.post(f"{API_URL}/chat/agent", json=payload, headers=HEADERS)
    resp.raise_for_status()
    data = resp.json()

    assistant_msg = None
    try:
        assistant_msg = data["choices"][0]["message"]["content"]
    except Exception:
        assistant_msg = json.dumps(data, ensure_ascii=False)

    return assistant_msg, data

# FUNÇÃO PARA DEFINIR FILTROS DE BUSCA
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

# FUNÇÃO PANDAS PARA BUSCA DE DADOS
def buscar_dados(filtros):
    df = pd.read_excel('backend\src\data.xlsx', dtype=object)
    target = filtros

    mask = df.applymap(lambda x: isinstance(x, str) and any(t in x for t in target))

    filtered_df = df[mask.any(axis=1)]
    
    busca_info = filtered_df.to_json(orient="records")

    return busca_info

if __name__ == "__main__":
    while True:
        user_msg = input("Você: ").strip()

        filtros = definir_filtros(user_msg)

        sys_msg = buscar_dados(filtros)
        print(sys_msg)

        assistant_msg, data = enviar_mensagem(sys_msg, user_msg)

        print(f"\nAssistente: {assistant_msg}\n")