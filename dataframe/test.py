import unittest
from newsdata import *
from datetime import datetime
import json


class Test(unittest.TestCase):
    def test_findCompany(self):
        title = "Netflix Hires Activision CFO - WSJ"
        result = findCompany(title)
        self.assertEqual(result, [("Netflix", "NFLX", "NASDAQ")])

    def test_findCompany2(self):
        title = "Netflix fucks Microsoft"
        result = findCompany(title)
        self.assertCountEqual(
            result, [("Netflix", "NFLX", "NASDAQ"), ("Microsoft", "MSFT", "NASDAQ")]
        )

    def test_makeRowsFromArticle(self):
        with open("result201901.json", "r") as jf:
            articleJson = json.load(jf)[0]
        result = makeRowsFromArticle(articleJson, articleJson["title"], [0])

    def test_rightTime(self):
        articleDatetime = datetime.strptime("2019-01-01T04:39:00", "%Y-%m-%dT%H:%M:%S")

        self.assertTrue(rightTime(articleDatetime))

    def test_wrongTime(self):
        articleDatetime = datetime.strptime("2005-01-01T04:39:00", "%Y-%m-%dT%H:%M:%S")
        self.assertFalse(rightTime(articleDatetime))

if __name__ == "__main__":
    unittest.main()
