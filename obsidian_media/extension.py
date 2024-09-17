# SPDX-FileCopyrightText: © 2024 Serhii “GooRoo” Olendarenko
# SPDX-License-Identifier: BSD-3-Clause

import logging
import markdown
import re
from urllib.parse import urlparse, unquote
import xml.etree.ElementTree as etree

from markdown.treeprocessors import Treeprocessor
from pathlib import Path

logger = logging.getLogger(f'markdown.extensions.{__name__}')


class ObsidianMediaEmbedder(Treeprocessor):
    # from https://help.obsidian.md/Files+and+folders/Accepted+file+formats:
    OBSIDIAN_FORMATS = {
        # images
        'avif': 'image/avif',
        'bmp': 'image/bmp',
        'gif': 'image/gif',
        'jpeg': 'image/jpeg',
        'jpg': 'image/jpeg',
        'png': 'image/png',
        'svg': 'image/svg+xml',
        'webp': 'image/webp',
        # audio
        'mp3': 'audio/mpeg',
        'wav': 'audio/wav',
        'm4a': 'audio/mp4',
        'ogg': 'audio/ogg',
        '3gp': 'audio/3gpp',
        'flac': 'audio/flac',
        # video
        'mp4': 'video/mp4',
        'webm': 'video/webm',
        'ogv': 'video/ogg',
        'mov': 'video/quicktime',
        'mkv': 'video/x-matroska',
    }

    ALT_REGEX = re.compile(r'^(\d+)(?:x(\d+))?$')

    def file_path(self, src) -> Path:
        return Path(urlparse(src).path)

    def file_mime(self, path: Path) -> str | None:
        file_format = path.suffix[1:].lower()
        return self.OBSIDIAN_FORMATS.get(file_format)

    def file_type(self, path: Path) -> str | None:
        mime = self.file_mime(path)
        return mime.split('/')[0] if mime is not None else None

    def run(self, root):
        for element in root.iter('img'):
            match attributes := element.attrib:
                case {'src': str(src), 'alt': str(alt)} if self.file_type(path := self.file_path(src)) == 'image':
                    if (alt_match := re.match(self.ALT_REGEX, alt)) is not None:
                        width, height = alt_match.groups()
                        element.set('width', width)
                        if height is not None:
                            element.set('height', height)
                        element.set('alt', path.name)
                    pass

                case {'src': str(src)} if src != '' and (tag := self.file_type(path := self.file_path(src))) in [
                    'audio',
                    'video',
                ]:
                    tail = element.tail
                    element.clear()
                    element.tag = tag
                    element.tail = tail

                    element.text = 'Your browser does not support this type of media.'

                    element.set('style', 'width: 100%')

                    media_link = etree.SubElement(element, 'a')
                    media_link.set('href', src)
                    media_link.text = f'../{unquote(src)}'

                    element.set('controls', '1')

                    source = etree.SubElement(element, 'source')
                    # The thing here is that MkDocs adjusts img.src and a.href automatically, however, it doesn't
                    # touch source.src, so we have to prepend with '../' manually.
                    source.set('src', f'../{src}')
                    source.set('type', self.file_mime(path) or '')

                    for k, v in (attr for attr in attributes.items() if attr[0] not in ['src']):
                        element.set(k, v)


class ObsidianMediaExtension(markdown.extensions.Extension):
    def extendMarkdown(self, md):
        md.treeprocessors.register(ObsidianMediaEmbedder(md), 'obsidianemdiaembedder', 15)
