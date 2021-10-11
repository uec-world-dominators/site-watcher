import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import unittest

import watchcat.__main__
from watchcat.resource.http_resource import HttpResource


class Test(unittest.TestCase):
    def test_main(self):
        watchcat.__main__.main()

    def test_http_resource(self):
        pass


if __name__ == "__main__":
    unittest.main()
