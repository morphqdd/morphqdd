import unittest

from update_readme_gif import update_readme_gif


SAMPLE = (
    '<div align="center">\n'
    '  <img height="" src="https://example.com/old.gif"  />\n'
    '</div>\n'
)


class UpdateReadmeGifTests(unittest.TestCase):
    def test_replaces_header_src(self):
        result = update_readme_gif(SAMPLE, "https://example.com/new.gif")
        self.assertIn('src="https://example.com/new.gif"', result)
        self.assertNotIn("old.gif", result)

    def test_preserves_surrounding_markup(self):
        result = update_readme_gif(SAMPLE, "https://example.com/new.gif")
        self.assertTrue(result.startswith('<div align="center">\n'))
        self.assertIn('</div>\n', result)

    def test_same_url_is_noop_but_valid(self):
        result = update_readme_gif(SAMPLE, "https://example.com/old.gif")
        self.assertEqual(result, SAMPLE)

    def test_only_replaces_first_img(self):
        text = SAMPLE + '<img height="" src="https://example.com/second.gif"  />\n'
        result = update_readme_gif(text, "https://example.com/new.gif")
        self.assertIn('src="https://example.com/new.gif"', result)
        self.assertIn('src="https://example.com/second.gif"', result)

    def test_raises_when_no_header_img(self):
        with self.assertRaises(ValueError):
            update_readme_gif("<div>no image here</div>\n", "https://example.com/new.gif")


if __name__ == "__main__":
    unittest.main()
