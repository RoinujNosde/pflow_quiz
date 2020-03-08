import json
from urllib import request, error

quizes_url = "https://roinujnosde.pythonanywhere.com/quizes/"
detalhe_quiz_url = "https://roinujnosde.pythonanywhere.com/quizes/%d/"

def pegar_dados_do_quiz(id):
    """Acessa a URL externa, baixa informações sobre o Quiz com o ID informado e as retorna"""
    url = detalhe_quiz_url % int(id)
    try:
        with request.urlopen(url) as response:
            data = json.loads(response.read())
    except(error.URLError):
        return None

    #Remove as não aprovadas da lista
    data['pergunta_set'][:] = [pergunta for pergunta in data['pergunta_set'] if pergunta['aprovada']]
    return data

def pegar_list_de_quizes(tree):
    """Acessa a URL externa, baixa informações sobre os quizes e os retorna"""
    try:
        with request.urlopen(quizes_url) as response:
            data = json.loads(response.read())
            return data
    except(error.URLError):
        return None
