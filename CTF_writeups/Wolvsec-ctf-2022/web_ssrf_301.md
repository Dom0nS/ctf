# Web: SSRF 301

![image](https://user-images.githubusercontent.com/74207547/160584776-1310eb04-8e10-4fd1-a0b2-c3a69b078f19.png)

It's a harder version of [SSRF 101](ctf/CTF_writeups/Wolvsec-ctf-2022/web_ssrf_101.md)

## Differences in source code

>## public.js
```js
app.get('/ssrf', (req, res) => {
    const path = req.query.path
    if (typeof path !== 'string' || path.length === 0) {
        res.send('path must be a non-empty string')
    }
    else {
        const normalizedPath = path.normalize('NFKC')
        const firstPathChar = normalizedPath.charAt(0)
        if ('0' <= firstPathChar && firstPathChar <= '9') {
            res.send('first chararacter of path must not normalize to a digit')
        }
        else {
            const url = `http://localhost:${private1Port}${normalizedPath}`
            const parsedUrl = new URL(url)
    
            if (parsedUrl.hostname !== 'localhost') {
                // Is it even possible to get in here???
                res.send('sorry, you can only talk to localhost')
            }
            else {
                // Make the request and return its content as our content.
                http.get(parsedUrl.href, ssrfRes => {
                    let contentType = ssrfRes.headers['content-type']

                    let body = ''
                    ssrfRes.on('data', chunk => {
                        body += chunk
                    })

                    ssrfRes.on('end', () => {
                        if (contentType) {
                            res.setHeader('Content-Type', contentType)
                        }
                        res.send(body)
                    })
                }).on('error', function(e) {
                    res.send("Got error: " + e.message)
                })
            }
        }
    }
})
```
The only difference is that there is a check for the first character of the path parameter which cannot be a number. We can easily bypass this poor validation attempt.

##  HTTP/HTTPS basic authentication URL with @

HTTP/HTTPS protocol accept authentication using @ symbol with username and password `https://username:password@URL`

We can use it to send request with server hostname and port as username and password. After @ we can enter new hostname, port and path we want to visit.
Server will see the request as `https://localhost:10011@locahost:10011/flag`

![image](https://user-images.githubusercontent.com/74207547/160586864-b66c148d-0ac1-48a6-a6f8-021f9be004a5.png)

## CRLF injection - %0D%0A

The HTTP protocol uses the CRLF character sequence to signify where one header ends and another begins. In this case we can use it to bypass check for the first character.

`http//localhost:10011/
1/flag
`
![image](https://user-images.githubusercontent.com/74207547/160588368-80d06429-4308-486f-8eb5-eb5fb4e7e985.png)

## FLAG: wsc{url_synt4x_f0r_th3_w1n_hq32pl}
