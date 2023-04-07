import unittest

from storage.Dynamo import Dynamo


class TestDynamo(unittest.TestCase):
    def test_create(self):
        portfolio = {
                    "name": "allie",
                    "portfolio": [{"name": "og-bitcoin", "amount": 2, "id": "bitcoin"}]
                }
        resp = Dynamo.create_item('portfolioTest', portfolio)
        print(resp)

if __name__ == '__main__':
    unittest.main()
