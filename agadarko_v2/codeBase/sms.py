from sqlite3 import paramstyle
import requests


API_keys='03d1a827caadbed08d62b9f38e97b0ffde93c23a2a82e30ee75708e7fa8d6027'
params=''

def smscalls(MESSAGE,to):
    url='https://api.smsonlinegh.com/v4/message/sms/send?key='+API_keys+'&text='+MESSAGE+'&type=0&sender=MyDevTest&to='+to+''
    send=requests.get(url,headers={'Content-Type':'application/x-www-form-urlencoded','Accept':'application/json'})
    print(send.status_code)
    return send.status_code