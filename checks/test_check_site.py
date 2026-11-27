import unittest

from check_site import local_ref, parse_page, require_ref


class CheckSiteTest(unittest.TestCase):
    def test_query_and_encoded_filename(self):
        self.assertEqual(local_ref("index.html", "./%E7%85%A7%E7%89%87.html?v=3#top"), "照片.html")

    def test_nested_and_directory_links(self):
        self.assertEqual(local_ref("app/sop/index.html", "../"), "app/index.html")
        self.assertIsNone(local_ref("app/index.html", "https://example.invalid/missing.js"))
        self.assertIsNone(local_ref("app/index.html", "#local-section"))

    def test_broken_link_and_project_escape(self):
        with self.assertRaisesRegex(ValueError, "missing local reference"):
            require_ref("index.html", "./missing.html", {"index.html"})
        with self.assertRaisesRegex(ValueError, "outside"):
            local_ref("index.html", "/other-project/asset.js")
        with self.assertRaisesRegex(ValueError, "malformed"):
            local_ref("index.html", "./%2e%2e/asset.js")

    def test_unclosed_script(self):
        with self.assertRaisesRegex(ValueError, "closed script"):
            parse_page("<html><head></head><body><script>hello")

    def test_inert_inline_types_ignored(self):
        p = parse_page('<html><head></head><body><script type="application/json">{}</script>'
                       '<script type="module">export {};</script><script src="bundle.js"></script></body></html>')
        self.assertEqual(len(p.scripts), 1)
        self.assertEqual(p.refs, ["bundle.js"])


if __name__ == "__main__":
    unittest.main()
