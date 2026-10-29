"""Ensure installed references and offline showcase resources stay portable."""
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.ids.extend([attrs['id']] if 'id' in attrs else [])
        for key in ('href', 'src'):
            if key in attrs:
                self.links.append(attrs[key])


class PackageTests(unittest.TestCase):
    def assert_local_link(self, source, link):
        parsed = urlsplit(link)
        if parsed.scheme or parsed.netloc:
            return
        if parsed.path:
            target = (source.parent / unquote(parsed.path)).resolve()
            self.assertTrue(target.is_relative_to(ROOT), (source.name, link))
            self.assertTrue(target.is_file(), (source.name, link))

    def test_documentation_links_resolve_in_extracted_repository(self):
        for source in ROOT.rglob('*.md'):
            text = source.read_text(encoding='utf-8')
            for link in re.findall(r'\]\(([^\s)]+)\)', text):
                with self.subTest(source=source.relative_to(ROOT), link=link):
                    self.assert_local_link(source, link)

    def test_showcase_links_and_anchors_resolve_without_network_assets(self):
        source = ROOT / 'docs/index.html'
        parser = Links()
        text = source.read_text(encoding='utf-8')
        parser.feed(text)
        self.assertEqual(len(parser.ids), len(set(parser.ids)), 'Duplicate HTML IDs')
        for link in parser.links:
            with self.subTest(link=link):
                self.assert_local_link(source, link)
                if link.startswith('#'):
                    self.assertIn(link[1:], parser.ids)
        self.assertNotRegex(text, r'<(?:script|link|img)[^>]+(?:src|href)=["\']https?://')

    def test_skill_reference_links_survive_installing_only_skill_folder(self):
        skill = ROOT / 'skills/simulink-carsim-cosim'
        for source in skill.rglob('*.md'):
            for link in re.findall(r'\]\(([^\s)]+)\)', source.read_text(encoding='utf-8')):
                if not urlsplit(link).scheme:
                    target = (source.parent / unquote(urlsplit(link).path)).resolve()
                    self.assertTrue(target.is_relative_to(skill), (source.name, link))


if __name__ == '__main__':
    unittest.main()
