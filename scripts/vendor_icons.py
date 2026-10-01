#!/usr/bin/env python3
"""Fetch pinned icon sources and record their upstream provenance."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
from urllib.request import urlopen
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent / 'assets/icons'
BOOTSTRAP = 'https://raw.githubusercontent.com/twbs/icons/v1.13.1/'
DEVICON = 'https://raw.githubusercontent.com/devicons/devicon/v2.17.0/'
SOURCES = {name: BOOTSTRAP + f'icons/{upstream}.svg' for name, upstream in {
    'x': 'twitter-x', 'linkedin': 'linkedin', 'youtube': 'youtube',
    'spotify': 'spotify', 'github': 'github', 'files': 'folder-fill',
}.items()}
SOURCES['vscode'] = DEVICON + 'icons/vscode/vscode-plain.svg'
SOURCES['bootstrap-LICENSE.txt'] = BOOTSTRAP + 'LICENSE'
SOURCES['devicon-LICENSE.txt'] = DEVICON + 'LICENSE'


def fetch(item):
    name, url = item
    with urlopen(url, timeout=30) as response:
        data = response.read()
    if name.endswith('.txt'):
        return name, data
    # Normalize the upstream shapes to a single monochrome silhouette.
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    svg = ET.fromstring(data)
    for element in svg.iter():
        element.attrib.pop('style', None)
        if 'fill' in element.attrib:
            element.set('fill', '#f5f5f5')
    svg.set('fill', '#f5f5f5')
    svg.set('width', '32')
    svg.set('height', '32')
    return name + '.svg', ET.tostring(svg, encoding='utf-8')


def main():
    with ThreadPoolExecutor(max_workers=4) as pool:
        downloads = list(pool.map(fetch, SOURCES.items()))
    ROOT.mkdir(parents=True, exist_ok=True)
    for name, content in downloads:
        (ROOT / name).write_bytes(content)
    (ROOT / 'sources.json').write_text(json.dumps(SOURCES, indent=2) + '\n')
    print(f'Vendored {len(downloads) - 2} icons with upstream licenses')


if __name__ == '__main__':
    main()
