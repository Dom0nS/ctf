# Crypto: EAV-Secure Diffie–Hellman? 

![image](https://user-images.githubusercontent.com/74207547/160667986-80b6c87f-e3e5-4480-91cb-69c401e4a5cb.png)

## Source code review
>## key_exchange.py

```python
from Crypto.Util.number import bytes_to_long, long_to_bytes

# I love making homespun cryptographic schemes!

def diffie_hellman():
    f = open("flag.txt", "r")
    flag = f.read()
    a = bytes_to_long(flag.encode('utf-8'))
    #print(a)
    #print(long_to_bytes(a))
    p = 320907854534300658334827579113595683489
    g = 3
    A = pow(g,a,p) #236498462734017891143727364481546318401

if __name__ == "__main__":
    diffie_hellman()

# EAV-Secure? What's that?
```

![image](https://user-images.githubusercontent.com/74207547/160669265-1948faf9-b3d7-4fcd-aa8d-b328625dc9b9.png)

To solve this challenge we need to find exponent `x` value. The problem is well known as `The Discrete Logarithm Problem`. It is used in diffie hellman key exchange more about it [here](https://ir0nstone.gitbook.io/crypto/dhke/overview#the-discrete-logarithm-problem)

## Getting the flag

Because given numbers are relatively small we can try to calculate x value. I found [online calculator](https://www.alpertron.com.ar/DILOG.HTM) that worked.

![image](https://user-images.githubusercontent.com/74207547/160669771-f42999d1-71ea-4693-9db0-d9b139ff89ad.png)

The only step left is to write a Python script that will find the final value of x and decode it into our flag

```python
from Crypto.Util.number import bytes_to_long, long_to_bytes

for i in range(1,1000000000):
	a = 67514057458967447420279566091192598301
	b = 320907854534300658334827579113595683488
	flag = long_to_bytes(a+(b*i))
	if b"wsc{" in flag:
		print(flag)
		break
```

![image](https://user-images.githubusercontent.com/74207547/160670053-d2cc1ab1-5205-4516-b3ff-941b956b487c.png)

## FLAG: wsc{l0g_j4m_4tt4ck}
