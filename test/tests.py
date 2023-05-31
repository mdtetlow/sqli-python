import unittest
import os
import sys
sys.path.insert(0, os.path.abspath('./src'))
from bsqli import SqliHttpRequest


class TestSqliHttpRequest(unittest.TestCase):
  def setUp(self):
    self.req = SqliHttpRequest('https://foo.com', '{"Host": "foo.com", "Referer": "https://foo.com"}', '{"foo": "bar", "session": "ewjnvi34A_"}')
  
  def tearDown(self):
    self.req = None
  
  def test_create_request(self):
    self.assertEqual(self.req.url, 'https://foo.com')
    self.assertEqual(self.req.headers['Host'], 'foo.com')
    self.assertIsInstance(self.req.cookies, dict)
  
  def test_create_request_not_patch_header(self):
    req = SqliHttpRequest('https://foo.com', '{"Host": "random.io", "Referer": "http://bar.com"}', '{"foo": "bar", "session": "ewjnvi34A_"}')
    self.assertEqual(req.headers['Host'], 'random.io')
    self.assertEqual(req.headers['Referer'], 'http://bar.com')
  
  def test_create_request_patch_header_host(self):
    req = SqliHttpRequest('https://foo.com', '{"Host": "", "Referer": ""}', '{"foo": "bar", "session": "ewjnvi34A_"}')
    self.assertEqual(req.headers['Host'], 'foo.com')
    self.assertEqual(req.headers['Referer'], 'https://foo.com')
    
  @unittest.skip("removed method")
  def test_prepare_cookies(self):
    self.assertIsInstance(self.req._prepare_cookies('{"foo": "bar"}'), dict)
    self.assertEqual(self.req._prepare_cookies('{"foo": "bar"}'), {"foo": "bar"})
  
  @unittest.skip("removed method")
  def test_hostname(self):
    self.assertEqual(self.req._hostname('https://foo.com'), 'foo.com')
  
  def test_prepare_request_no_injection(self):
    headers, cookies = self.req._prepare_request()
    self.assertIsInstance(headers, dict)
    self.assertIsInstance(cookies, dict)
    self.assertEqual(headers['Host'], 'foo.com')
    self.assertEqual(headers['Referer'], 'https://foo.com')
    self.assertEqual(cookies['foo'], 'bar')
  
  def test_prepare_request_with_injection(self):
    self.req.inject('cookie', 'foo', "' AND '1' = '1")
    headers, cookies = self.req._prepare_request()
    self.assertIsInstance(headers, dict)
    self.assertIsInstance(cookies, dict)
    self.assertEqual(headers['Host'], 'foo.com')
    self.assertEqual(headers['Referer'], 'https://foo.com')
    self.assertEqual(cookies['foo'], "bar' AND '1' = '1")
  

  def test_inject(self):
    self.req.inject('cookie', 'foo', "' AND '1' = '1")
    self.req.inject('cookie', 'session', "' AND '1' = '2")
    self.req.inject('header', 'Referer', "' AND '1' = '2")
    self.assertIsInstance(self.req.injection, dict)
    self.assertEqual(self.req.injection['cookie']['foo'], "' AND '1' = '1")
    self.assertEqual(self.req.injection['cookie']['session'], "' AND '1' = '2")
    self.assertEqual(self.req.injection['header']['Referer'], "' AND '1' = '2")

  def test_prepare_injection(self):
    self.req.inject('cookie', 'foo', "' AND '1' = '1")
    self.req.inject('cookie', 'session', "' AND '1' = '2")
    self.req.inject('header', 'Referer', "' OR '1' = '1")
    headers, cookies = self.req._prepare_injection()
    self.assertIsInstance(cookies, dict)
    self.assertEqual(cookies['foo'], "bar' AND '1' = '1")
    self.assertEqual(cookies['session'], "ewjnvi34A_' AND '1' = '2")
    self.assertEqual(headers['Referer'], "https://foo.com' OR '1' = '1")
    
if __name__ == '__main__':
  unittest.main()
