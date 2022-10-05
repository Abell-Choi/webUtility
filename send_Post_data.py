import requests
from bs4 import BeautifulSoup as bs

req = requests.post('http://127.0.0.1:8080/convertmp4togif',data={
    'url' : 'https://ac-p.namu.la/07/072c467266db67120598d2cb13c1c1d308248da0728eeb85634783be3a3ab663.mp4'
})

print(req.content)