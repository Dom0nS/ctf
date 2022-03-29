# Web: Java???

![image](https://user-images.githubusercontent.com/74207547/160655244-8144468c-df98-49ed-9c02-ddd5bea50d14.png)

`Java has template engines too! -> First thought java SSTI`

## Website:

![image](https://user-images.githubusercontent.com/74207547/160655634-caf0e353-f164-4119-933a-f84b37a87b22.png)

![image](https://user-images.githubusercontent.com/74207547/160655701-b3767971-c376-441d-80ac-9ab97fd6d325.png)

Simple web application that prints user input. When it comes to SSTI I always try this payload `${{<%[%'"}}%\.` from [cobalt article](https://cobalt.io/blog/a-pentesters-guide-to-server-side-template-injection-ssti), but the site didn't behave differently. At this point I know it's not going to be typical SSTI challenge

## Source Code Review

>## ChallengeApp.java

```java
// learning: https://www.x5software.com/chunk
// source: https://github.com/tomj74/chunk-templates/releases/tag/release-3.6.1
import com.x5.template.Chunk;
import com.x5.template.Theme;

import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.Map;

public class ChallengeApp extends HttpServlet {

    // Java 15 has """ strings! (but we're not using that here) :(
    final static String INDEX_HTML =
            "<html>" +
            "    <body>" +
            "        <p>Please tell us a little about yourself:</p>" +
            "        <form action='submit' method='GET'>" +
            "            <label for='name'>Name:</label>" +
            "            <input type='text' id='name' name='name'><br><br>" +
            "            <label for='color'>Favorite Color:</label>" +
            "            <input type='text' id='color' name='color'><br><br>" +
            "            <input type='submit' value='Submit'>" +
            "        </form>" +
            "    </body>" +
            "</html>";

    final static String TEMPLATE_HTML =
            "<html>" +
            "    <body>" +
            "        <p>How are you {$name}?</p>" +
            "        <p>{$color} is also one of our favorites!</p>" +
            "    </body>" +
            "</html>";

    @Override
    protected void doGet(final HttpServletRequest request, final HttpServletResponse response)
            throws IOException {
        route(request, response);
    }

    // nobody routes this way in real apps :)
    private void route(final HttpServletRequest request, final HttpServletResponse response)
            throws IOException {
        String path = request.getServletPath();
        if ("/submit".equals(path)) {
            returnTemplatePage(request, response);
        }
        else {
            returnMainPage(response);
        }
    }

    private void returnMainPage(final HttpServletResponse response) throws IOException {
        response.getWriter().print(INDEX_HTML);
    }

    private void returnTemplatePage(final HttpServletRequest request, final HttpServletResponse response)
            throws IOException {
        Theme theme = new Theme();
        Chunk html = theme.makeChunk();
        html.append(TEMPLATE_HTML);

        Map<String, String[]> params = request.getParameterMap();
        for (String paramName: params.keySet()) {
            String[] paramValues = params.get(paramName);
            String paramValue = String.join("", paramValues);
            html.set(paramName, preventTrickery(paramValue));
        }

        String flag = System.getenv("FLAG");
        html.set("flag", flag);

        response.getWriter().print(html.toString());
    }

    private String preventTrickery(final String input) {
        return preventRecursiveTags(htmlEncode(input));
    }

    private String preventRecursiveTags(final String input) {
        return input.replace("$", "");
    }

    private String htmlEncode(final String input) {
        return input
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace("\"", "&quot;")
                .replace("'", "&#39;");
    }
}
```

* Our output is generated via `chunk template engine`
* We control input of ${name} and ${color}
* After generating the template, the `{$flag}` variable is being set
```java
String flag = System.getenv("FLAG");
html.set("flag", flag);
```
* The content of that variable is our flag
* There are filters on `&<>\'` and `$`

## Obtaining the flag

Without filters we could easily get the flag with ${flag} input. After spending some time trying to bypass the filters I gave up. I told myself there must be other way around it and started to read provided github link with the source of chunk template engine

![image](https://user-images.githubusercontent.com/74207547/160661717-c49dd5f6-e76f-42a6-a7e1-8f41142f78c7.png)

It turned out that in the github repo there is test folder with all the tests performed on the chunk template engine. I figured if there is other possibilty to work with variables, it must be in that folder

>## ChunkTest.java
```java
...
@Test
    public void testSimpleExpandWithTagDefaultAltSyntax()
    {
        Chunk c = new Chunk();
        c.append("Hello, my name is {~name:~full_name}!");
        c.unset("name");
        c.set("full_name","Bob Johnson");
        assertEquals("Hello, my name is Bob Johnson!",c.toString());
    }
...
```
I was right, here it is! We can use {~flag} to get the flag content

![image](https://user-images.githubusercontent.com/74207547/160663069-cfa55303-5ef1-41ec-b6cd-bbd40fbea105.png)

## FLAG: wsc{j4v4_ch4ls_4r3_r4r3_513156}



