# Web: SSRF 101

![image](https://user-images.githubusercontent.com/74207547/160583998-d4882e9c-07f9-43a8-870d-3a732eb78781.png)

We are given a source code

![image](https://user-images.githubusercontent.com/74207547/160570547-102b82f1-1b7b-41a0-912a-5213fb8b9617.png)

## Source code review

>## public.js

```js
const { URL } = require('url')
const http = require('http')
const express = require('express')
const app = express()
const publicPort = 80
const private1Port = 1001

app.get('/', (req, res) => {
    res.sendFile(__dirname + '/public.js')
})

// Use this endpoint to reach a web server which
// is only locally accessible. Try: /ssrf?path=/
app.get('/ssrf', (req, res) => {
    const path = req.query.path
    if (typeof path !== 'string' || path.length === 0) {
        res.send('path must be a non-empty string')
    }
    else {
        const url = `http://localhost:${private1Port}${path}`
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
})

// this port is exposed publicly 
app.listen(publicPort, () => {
  console.log(`Listening on ${publicPort}`)
})
```

Looks like we've got two endpoints:
* `/`- prints the source of public.js file
* `/ssrf` - with **path** param we can request a file from web root and the server will return its content

---
Let's search how we can obtain the flag

>## private2.js
```js
const express = require('express')
const app = express()
const private2Port = 10011

app.get('/', (req, res) => {
    res.sendFile(__dirname + '/private2.js')
})

app.get('/flag', (req, res) => {
    res.sendFile(__dirname + '/flag.txt')
})

// this port is only exposed locally
app.listen(private2Port, () => {
    console.log(`Listening on ${private2Port}`)
})
```

Request to the server on localport 10011 with /flag path will return flag content.
```js
const private1Port = 1001
...
// this port is exposed publicly 
app.listen(publicPort, () => {
  console.log(`Listening on ${publicPort}`)
})
```
Main web app is running on port 1001 which is weirdly similar. Let's see if we can leverage ssrf endpoint to have the server send a request to our flag.

```js
const path = req.query.path
    if (typeof path !== 'string' || path.length === 0) {
        res.send('path must be a non-empty string')
    }
    else {
        const url = `http://localhost:${private1Port}${path}`
        const parsedUrl = new URL(url)
```

The server only checks if the path is a string and is not empty. There is no slash between port and path values which can easily lead to ssrf

## Finding a way to read the flag 

Because there is no proper validation of user input we can inject additional `1` to the port number and then enter the path to the endpoint with our flag `/flag`. As the result of that server will make get request to `http://localhost:10011/flag`

![image](https://user-images.githubusercontent.com/74207547/160579438-a61416ea-024c-493e-923e-3324c627d608.png)

## FLAG: wsc{ssrf_c4n_b3_fun_xl9m782}
