import unittest

from select_gif import select_gif


RULES = {
    "default": "default.gif",
    "div2": "two.gif",
    "div3": "three.gif",
    "div5": "five.gif",
}


class SelectGifTests(unittest.TestCase):
    def test_zero_is_default(self):
        self.assertEqual(select_gif(0, RULES), RULES["default"])

    def test_one_is_default(self):
        self.assertEqual(select_gif(1, RULES), RULES["default"])

    def test_two_is_div2(self):
        self.assertEqual(select_gif(2, RULES), RULES["div2"])

    def test_three_is_div3(self):
        self.assertEqual(select_gif(3, RULES), RULES["div3"])

    def test_five_is_div5(self):
        self.assertEqual(select_gif(5, RULES), RULES["div5"])

    def test_six_div2_and_div3_picks_div3(self):
        self.assertEqual(select_gif(6, RULES), RULES["div3"])

    def test_ten_div2_and_div5_picks_div5(self):
        self.assertEqual(select_gif(10, RULES), RULES["div5"])

    def test_fifteen_div3_and_div5_picks_div5(self):
        self.assertEqual(select_gif(15, RULES), RULES["div5"])

    def test_thirty_div2_div3_div5_picks_div5(self):
        self.assertEqual(select_gif(30, RULES), RULES["div5"])

    def test_seven_is_default(self):
        self.assertEqual(select_gif(7, RULES), RULES["default"])


if __name__ == "__main__":
    unittest.main()
