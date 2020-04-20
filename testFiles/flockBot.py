import requests

url = 'https://api.flock.com/hooks/sendMessage/f63980ee-4add-4b5f-87ce-ab024b58cc72'
myobj = {'text': 'Test msg'}

x = requests.post(url, json = myobj)

print(x.text)