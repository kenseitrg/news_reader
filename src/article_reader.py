import requests
from readability import Document


def text_from_url(url: str) -> str:
    response = requests.get(url)
    if response.ok:
        doc = Document(response.text)
        return doc.summary()
    else:
        return "Can not get article text"
