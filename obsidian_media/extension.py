# SPDX-FileCopyrightText: © 2024 Serhii “GooRoo” Olendarenko
# SPDX-License-Identifier: BSD-3-Clause

import itertools
import logging
import re
import xml.etree.ElementTree as etree
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

import markdown
from markdown.treeprocessors import Treeprocessor

# logger = logging.getLogger(f'mkdocs.plugins.{__name__}')
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

    ALT_SIZE_REGEX = re.compile(r'^(\d+)(?:x(\d+))?$')

    def file_path(self, src) -> Path:
        return Path(urlparse(src).path)

    def file_mime(self, path: Path) -> str | None:
        file_format = path.suffix[1:].lower()
        return self.OBSIDIAN_FORMATS.get(file_format)

    def file_type(self, path: Path) -> str | None:
        mime = self.file_mime(path)
        return mime.split('/')[0] if mime is not None else None

    def youtube_video(self, src: str) -> str | None:
        url = urlparse(src)
        if url.netloc == 'youtu.be':
            return url.path[1:]
        elif url.netloc == 'www.youtube.com':
            return parse_qs(url.query).get('v', [None])[0]
        else:
            return None

    def run(self, root):
        for element in root.iter('img'):
            match attributes := element.attrib:
                case {'src': str(src), 'alt': str(alt)} if self.file_type(path := self.file_path(src)) == 'image':
                    self.adjust_image(element, path, alt)

                case {'src': str(src)} if src != '' and (tag := self.file_type(path := self.file_path(src))) in [
                    'audio',
                    'video',
                ]:
                    self.replace_with_media_file(element, attributes, tag, src, path)

                case {'src': str(src), 'alt': alt} if (v := self.youtube_video(src)) is not None:
                    self.replace_with_youtube_video(element, v, alt)

    def replace_with_media_file(
        self, element: etree.Element, attributes: dict[str, str], tag: str, src: str, path: Path
    ):
        logger.info(f'The image points to {tag}. Replacing with media file.')

        tail = element.tail
        element.clear()
        element.tag = tag
        element.tail = tail

        element.text = 'Your browser does not support this type of media.'

        element.set('style', 'width: 100%')

        media_link = etree.SubElement(element, 'a')
        media_link.set('href', src)
        media_link.text = f'{unquote(src)}'

        element.set('controls', '1')

        source = etree.SubElement(element, 'source')
        source.set('src', f'{src}')
        source.set('type', self.file_mime(path) or '')

        for k, v in (attr for attr in attributes.items() if attr[0] not in ['src']):
            element.set(k, v)

    def adjust_image(self, element: etree.Element, path: Path, alt: str):
        """If the alt text contains size, set it for HTML element."""
        if (alt_match := re.match(self.ALT_SIZE_REGEX, alt)) is not None:
            width, height = alt_match.groups()
            element.set('width', width)
            if height is not None:
                element.set('height', height)
            element.set('alt', path.name)

    def replace_with_youtube_video(self, element: etree.Element, video_id: str, alt: str | None):
        logger.info('The image points to a YouTube video. Replacing with <iframe>.')

        element.clear()
        element.tag = 'iframe'
        element.set('style', 'width: 100%; height: auto; aspect-ratio: 16 / 9;')
        element.set('src', f'https://www.youtube.com/embed/{video_id}')
        element.set('frameborder', '0')
        element.set(
            'allow',
            'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share',
        )
        element.set('referrerpolicy', 'strict-origin-when-cross-origin')
        element.set('allowfullscreen', '1')
        element.set('title', alt or '')


class AudioVideoSourceProcessor(Treeprocessor):
    """Adjusts relative paths in audio and video source elements."""

    def run(self, root: etree.Element):
        for element in itertools.chain(root.findall('.//audio/source[@src]'), root.findall('.//video/source[@src]')):
            src = element.attrib['src']
            logger.debug(f'Adjusting {src} to ../{src}')
            if self.is_relative(src):
                element.set('src', f'../{src}')

    def is_relative(self, src: str) -> bool:
        url = urlparse(src)
        return url.scheme == '' and url.netloc == ''


class ObsidianMediaExtension(markdown.extensions.Extension):
    def extendMarkdown(self, md):
        md.treeprocessors.register(ObsidianMediaEmbedder(md), 'ObsidianMediaEmbedder', priority=10)


class ObsidianMediaMkDocsExtension(markdown.extensions.Extension):
    def extendMarkdown(self, md):
        md.treeprocessors.register(AudioVideoSourceProcessor(md), 'AudioVideoSourceProcessor', priority=9)
        md.treeprocessors.register(ObsidianMediaEmbedder(md), 'ObsidianMediaEmbedder', priority=10)
