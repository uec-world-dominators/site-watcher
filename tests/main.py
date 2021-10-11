import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import watchcat.__main__
import unittest

class Test(unittest.TestCase):
    def test_main(self):
        watchcat.__main__.main()

if __name__ == '__main__':
    unittest.main()
