import requests
from bs4 import BeautifulSoup

def check_nif(nif: str) -> str:
    session = requests.Session()
    get_url = 'https://portaldocontribuinte.minfin.gov.ao/consultar-headNifId-do-contribuinte'
    response_get = session.get(get_url, verify=False)

    if response_get.status_code != 200:
        return f"GET request failed with status code: {response_get.status_code}"
    soup = BeautifulSoup(response_get.text, 'html.parser')
    view_state = soup.find('input', {'name': 'javax.faces.ViewState'})['value']

    headers = {
        'Accept': 'application/xml, text/xml, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Faces-Request': 'partial/ajax',
        'Origin': 'https://portaldocontribuinte.minfin.gov.ao',
        'Referer': get_url,
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
    }

    data = {
        'javax.faces.partial.ajax': 'true',
        'javax.faces.source': 'j_id_2x:j_id_34',
        'javax.faces.partial.execute': 'j_id_2x',
        'javax.faces.partial.render': 'showpanelNIF',
        'j_id_2x:j_id_34': 'j_id_2x:j_id_34',
        'j_id_2x:txtNIFNumber': nif,
        'j_id_2x_SUBMIT': '1',
        'javax.faces.ViewState': view_state,  
    }

    post_url = 'https://portaldocontribuinte.minfin.gov.ao/consultar-headNifId-do-contribuinte'
    response_post = session.post(post_url, headers=headers, data=data, verify=False)

    if response_post.status_code != 200:
        return f"POST request failed with status code: {response_post.status_code}"
    if "NIF não encontrado" in response_post.text:
        return False
    else:
        return True

nif = input("Enter NIF: ")
result = check_nif(nif)
print(result)
