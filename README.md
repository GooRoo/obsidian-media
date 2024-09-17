<!--
SPDX-FileCopyrightText: © 2024 Serhii “GooRoo” Olendarenko

SPDX-License-Identifier: BSD-3-Clause
-->

# [Obsidian][obsidian] media embedder

[![Made by Ukrainian](https://img.shields.io/static/v1?label=Made%20by&message=Ukrainian&labelColor=1f5fb2&color=fad247&style=flat-square)](https://savelife.in.ua/en/donate-en/#donate-army-card-once)
[![License](https://img.shields.io/github/license/GooRoo/obsidian-media?style=flat-square)](LICENSE)

This is an extension for [Python-Markdown][python-markdown] which allows you to embed **audio** or **video** files as easily as images by simply writing:

```markdown
![my song](assets/music/my-last-song.mp3)
![my video](assets/video/interview.webm)
```

Additionally, this plugins allows to specify an image size [the Obsidian way](https://help.obsidian.md/Linking+notes+and+files/Embed+files#Embed+an+image+in+a+note), e.g.:

```markdown
![400x300](assets/images/photo.jpg)  <!-- width and height -->
![400](assets/images/photo.jpg)      <!-- only width -->
```

Supported formats are:
- **Images:**	`avif`, `bmp`, `gif`, `jpeg`, `jpg`, `png`, `svg`, `webp`.
- **Audio:** `mp3`, `wav`, `m4a`, `ogg`, `3gp`, `flac`.
- **Video:** `mp4`, `webm`, `ogv`, `mov`, `mkv`.
- **Other:** ~~`md`, `pdf`~~ _not yet._

## MkDocs

It can be used with [MkDocs][mkdocs] as following:

```yaml
# mkdocs.yml
markdown_extensions:
  - obsidian_media
```

For the best results, I recommend using it together with my [**mkdocs-obsidian-bridge**](https://github.com/GooRoo/mkdocs-obsidian-bridge). This would allow you to simply write:
```markdown
![[assets/audio/my favourite song.mp3]]
![[assets/video/birthday party.mov]]

![[images/photo.jpg|400x300]]
![[images/photo.jpg|200]]
```

## Credits

This extension is heavily inspired by [orobardet/pymarkdown-video](https://github.com/orobardet/pymarkdown-video) and motivated by @pipe-organ in GooRoo/mkdocs-obsidian-bridge#17.


[mkdocs]: https://www.mkdocs.org
[obsidian]: https://obsidian.md
[python-markdown]: https://python-markdown.github.io/
