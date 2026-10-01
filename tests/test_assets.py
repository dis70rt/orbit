import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET
from orbit.icons import IconResolver, ASSET_ROOT
from orbit.settings import Settings

ROOT = Path(__file__).resolve().parent.parent


class AssetTests(unittest.TestCase):
    def test_default_shortcuts_have_unique_dedicated_monochrome_assets(self):
        settings = Settings.load(ROOT / 'config/default.json')
        self.assertEqual([s.label for s in settings.shortcuts],
                         ['X', 'LinkedIn', 'YouTube', 'Spotify', 'VS Code', 'GitHub', 'Files'])
        paths = [IconResolver.resolve(s.icon) for s in settings.shortcuts]
        self.assertEqual(len(set(paths)), 7)
        for path in paths:
            svg = ET.parse(path).getroot()
            self.assertIn('viewBox', svg.attrib)
            self.assertEqual(svg.attrib['fill'], '#f5f5f5')
            self.assertTrue(any(e.tag.endswith('path') for e in svg.iter()))
            self.assertTrue(all(e.attrib.get('fill', '#f5f5f5') == '#f5f5f5' for e in svg.iter()))

    def test_theme_names_and_unknown_bundled_names(self):
        self.assertIsNone(IconResolver.resolve('folder-symbolic'))
        with self.assertRaises(ValueError):
            IconResolver.resolve('bundled:../../private')
        with self.assertRaises(FileNotFoundError):
            IconResolver.resolve('/missing/icon.svg')

    def test_version_metadata_is_consistent(self):
        from orbit import __version__
        self.assertEqual((ROOT / 'VERSION').read_text().strip(), __version__)
        self.assertTrue(__version__.startswith('0.'))

    def test_provenance_and_licenses_are_shipped(self):
        sources = json.loads((ASSET_ROOT / 'sources.json').read_text())
        self.assertEqual(len(sources), 9)
        for name in ('bootstrap', 'devicon'):
            license_text = (ASSET_ROOT / f'{name}-LICENSE.txt').read_text()
            self.assertIn('Permission is hereby granted', license_text)

    def test_accessibility_options_validate_types(self):
        data = json.loads((ROOT / 'config/default.json').read_text())
        for key in ('show_label', 'animations'):
            with self.assertRaises(ValueError):
                Settings.from_dict({**data, key: 'false'})
        self.assertFalse(Settings.from_dict({**data, 'animations': False}).animations)
