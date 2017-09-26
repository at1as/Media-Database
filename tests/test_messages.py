from contextlib import contextmanager
from cStringIO import StringIO
from src.message import Message
import sys
import unittest

# Captures STDOUT in a variable
@contextmanager
def capture(command, *args, **kwargs):
  out, sys.stdout = sys.stdout, StringIO()
  try:
    command(*args, **kwargs)
    sys.stdout.seek(0)
    yield sys.stdout.read()
  finally:
    sys.stdout = out


class TestMessages(unittest.TestCase):
  
  def setUp(self):
    pass
  
  def tearDown(self):
    pass

  def test_success_message(self):
    text_string = "hello world"
    newline = "\n"
    green = "\x1b[92m"
    clear = "\x1b[0m"

    with capture(Message.success, text_string) as output:
      expected_output = "{}{}Success: {}{}{}".format(green, newline, clear, text_string, newline)
 
      self.assertEquals(expected_output, output)
  
  def test_warn_message(self):
    text_string = "hello world"
    newline = "\n"
    yellow = "\x1b[93m"
    clear = "\x1b[0m"

    with capture(Message.warn, text_string) as output:
      expected_output = "{}{}Warning: {}{}{}".format(yellow, newline, clear, text_string, newline)
 
      self.assertEquals(expected_output, output)
  
  def test_error_message(self):
    text_string = "hello world"
    newline = "\n"
    red = "\x1b[91m"
    clear = "\x1b[0m"

    with capture(Message.error, text_string) as output:
      expected_output = "{}{}Error: {}{}{}".format(red, newline, clear, text_string, newline)

      self.assertEquals(expected_output, output)

