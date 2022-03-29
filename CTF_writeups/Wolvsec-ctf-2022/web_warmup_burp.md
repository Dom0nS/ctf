# Web: Warmup Burp 

![image](https://user-images.githubusercontent.com/74207547/160458728-76f0b409-83fc-486e-a5f4-28228eaa4e61.png)

```As the name of the chall suggests Burp Suite will be a good tool to use```

## Web:

![image](https://user-images.githubusercontent.com/74207547/160460095-67d55ff5-ea8c-47ff-aa14-d5f40996dd06.png)

* After entering the URL we are redirected to youtube

## Burp Suite:

![image](https://user-images.githubusercontent.com/74207547/160461729-86ec1a9b-04b0-42d5-b9a6-fe57b3389f3c.png)
![image](https://user-images.githubusercontent.com/74207547/160461973-d976ccf9-9ecf-4f89-8210-fa568cc220bf.png)

I intercepted the traffic and added challenge address to the scope
* Before redirection we sent multiple get requests to the site with **flag** and **count** params
* Every response to the requests with count param contained **interesting header** <br>(base64 d3JvbmcgcGFnZS4uLnJlZGlyZWN0aW5n= -> "wrong page...redirecting")<br>
* What will happen if we send get request to the flag endpoint without **count** parameter?

![image](https://user-images.githubusercontent.com/74207547/160464227-dfa882f5-5558-457b-b6e3-f50fc14deb94.png)

Looks like something changed. The server is setting our cookie to **password=NONE** and the hint says **password: "DESSERT"**

![image](https://user-images.githubusercontent.com/74207547/160464604-04cf4afb-381a-4fec-850e-2dcdd5993486.png)

After sending request with the cookie **PASSWORD=DESSERT** we get the flag

## FLAG: wsc{c00k1e5_yum!}
