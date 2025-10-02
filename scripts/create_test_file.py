import os

test_content = '''# -*- coding: utf-8 -*-
import pytest

def test_minimal():
    assert True
'''

test_file_path = os.path.join('tests', 'test_error_handler.py')
with open(test_file_path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(test_content) 