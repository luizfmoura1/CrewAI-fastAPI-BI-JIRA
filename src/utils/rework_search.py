def rework_search(data: dict) -> list:
    cancelados = []
    for i in data['issues']:
        if i['fields']['status']['name'] == 'Cancelado':
            cancelados.append(i['id'])

    return cancelados
