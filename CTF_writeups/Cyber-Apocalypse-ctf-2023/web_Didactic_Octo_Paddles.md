#  Didactic Octo Paddles (medium)

> You have been hired by the Intergalactic Ministry of Spies to retrieve a powerful relic that is believed to be hidden within the small paddle shop, by the river. You must hack into the paddle shop's system to obtain information on the relic's location. Your ultimate challenge is to shut down the parasitic alien vessels and save humanity from certain destruction by retrieving the relic hidden within the Didactic Octo Paddles shop.


A web application built on Node.js is at our disposal, enabling us to create an account and sign in. Furthermore, we can add items to a virtual cart and view them as a list.

![image-20230318222803788](https://user-images.githubusercontent.com/74207547/227796403-c1470828-94ad-4294-bbb5-2bab4e5da8a9.png)

By examining the source code, we can observe the presence of an admin route that can only be accessed by a user with administrative privileges.

![image](https://user-images.githubusercontent.com/74207547/227798065-1d95e528-16b4-4486-ab33-9f8d62eed9cc.png)

After reviewing the admin endpoint, we can tell that we don't have admin access.

![image](https://user-images.githubusercontent.com/74207547/227798308-b34209cb-fca9-4d78-93a6-832c61457858.png)

Let's examine the AdminMiddleware file to understand how the verification of admin privileges is being managed.

![test](https://user-images.githubusercontent.com/74207547/227798971-0a204c90-a99e-49a6-8292-ff3e01b9ee12.png)

Authorization is handled with jwt tokens. 
If we manage to skip the first check of the token algorithm, our token will be checked against the null private key. 
There is a great article about the [security of jwt tokens](https://portswigger.net/web-security/jwt)

## Passing the string check

The server only checks if the header of the jwt token algorithm is equal to none but does not transform the algorithm entered by the user to lowercase. 
We can mix lowercase and uppercase to bypass the check. 
Also it is important to set `id` to `1` and delete the last part of jwt token, because without it, we will invoke an error caused by check against null private key.

Example token after decryption:

```
{"alg":"nOnE","typ":"JWT"}.{"id":1,"iat":1679152471,"exp":1679156071}.
```

Visiting admin page with forged token

![image](https://user-images.githubusercontent.com/74207547/227800194-cbc34b8c-0444-4d77-bb0d-7a72a4346170.png)

## Getting the flag

The flag is placed as a local file so we need LFI or some kind of RCE to read it.

After looking again at the endpoints in the source code, I noticed that the usernames on the admin page are rendered using the jsrender engine.

![image](https://user-images.githubusercontent.com/74207547/227800388-9843e42e-c1ee-4bfa-bbcd-0a7796430cd2.png)

Simple SSTI payload did the work

```
{{:"give_me_flag".toString.constructor.call({},"return global.process.mainModule.constructor._load('child_process').execSync('cat /flag.txt').toString()")()}}
```

![image](https://user-images.githubusercontent.com/74207547/227800598-bb37f2d1-d4e8-4782-9a8a-1dae7a222a86.png)

```
HTB{Pr3_C0MP111N6_W17H0U7_P4DD13804rD1N6_5K1115}
```
