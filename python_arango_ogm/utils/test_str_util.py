import logging
from python_arango_ogm.utils.str_util import squish_text, snake_text, title_text


TEST_INPUT = """
  Foo {


    Bar {
      Baz[]
    }

  }
"""

def test_squish():
  squished = squish_text(TEST_INPUT)
  logging.info(squished)
  assert squished == 'Foo{ Bar{ Baz[] } }'

def test_snake():
  # assert snake_text('foo!@#!&*^&&!@bar') == 'foo_bar'
  assert snake_text('BarFood') == 'bar_food'

def test_title():
  assert title_text('FooBar') == 'Foo Bar'
  assert title_text('fooBar') == 'Foo Bar'
  assert title_text('foo_bar') == 'Foo Bar'
  assert title_text('ABC') == 'ABC'
