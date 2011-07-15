import unittest

import test_actions
import test_couchdb

def suite():
    suite = unittest.TestSuite()
    suite.addTest(test_actions.suite())
    suite.addTest(test_couchdb.suite())
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
