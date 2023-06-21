import re
from functools import lru_cache

import bibtexparser
import requests
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode
from iguala import cond, match, regex
from mistletoe import Document
from mistletoe.block_token import Heading
from mistletoe.span_token import RawText

from ..fs import RepositoryFile
from .citations import APA_REGEXP, APACitation, BibtexCitation


class MarkdownDescription(RepositoryFile):
    IMG_REGEX = r"((?!http)|https://github\.com|https://user-images\.githubusercontent\.com)(?!.*(badge)).*?\.(gif|png|jpeg|jpg|svg)$"

    def __init__(self, raw_content, file):
        super().__init__(file)
        self.raw_content = re.sub("(<!--.*?-->)", "", raw_content, flags=re.DOTALL)
        self.content = Document(self.raw_content)

    @classmethod
    def from_file(cls, file):
        try:
            with file.open(encoding="utf-8", errors="surrogateescape"):
                content = file.read_text(encoding="utf-8")
            return cls(content, file)
        except FileNotFoundError:
            return cls("", file)

    @property
    def title(self):
        pattern = match(Document) % {
            "children": match(Heading) % {"level": 1, "children>content": "@title"}
        }
        result = pattern.match(self.content)
        if result.is_match:
            return result.bindings[0]["title"]
        return None

    @property
    def has_videos(self):
        pattern = match(Document) % {
            "children+>content": regex(r"^http(s)?://.*?\.(mp4|avi|mpeg)$")
        }
        result = pattern.match(self.content)
        return result.is_match

    @property
    def has_screenshots(self):
        pattern = match(Document) % {"children+>src": regex(self.IMG_REGEX)}
        result = pattern.match(self.content)
        if result.is_match:
            return True

        def is_img(__self__):
            e = __self__
            if "<img" not in e:
                return False
            img_pattern = re.compile(self.IMG_REGEX)
            tags = e.split()
            for tag in tags:
                if not tag.startswith("src"):
                    continue
                tag = tag[5:-1]
                return img_pattern.match(tag) is not None

        pattern = match(Document) % {"children+>content": cond(is_img)}
        result = pattern.match(self.content)
        return result.is_match

    @property
    def has_videos_or_screenshots(self):
        return self.has_videos or self.has_screenshots

    @property
    def has_usage(self):
        pattern = match(Document) % {
            "children": match(Heading)
            % {
                "level": range(2, 5),  # Must be a heading of at least 2
                "children*>content": regex(
                    r"^.*?[Uu]sage"  # Must contain "usage" in the title
                ),
            }
        }
        result = pattern.match(self.content)
        return result.is_match

    @property
    def has_installation(self):
        pattern = match(Document) % {
            "children+>content": regex(
                r"^.*?(pip|conda)\s+install"  # Must contain "pip install"
            ),
        }
        result = pattern.match(self.content)
        return result.is_match

    @property
    def has_intro(self):
        pattern = match(Document) % {
            "children": [
                ...,
                match(Heading) % {"level": 1},
                "*paragraphs",
                match(Heading) % {"level": 2},
                ...,
            ]
        }
        result = pattern.match(self.content)
        if result.is_match:
            paragraphs = result.bindings[0]["paragraphs"]

            def is_txt(p):
                if not hasattr(
                    p, "children"
                ):  # pragma: no cover, weird behavior that only happens on one file for weird reasons
                    return False
                for child in p.children:
                    if not isinstance(child, RawText):
                        continue
                    if child.content.startswith("<") or child.content[-1] == ">":
                        continue
                    return True
                return False

            return len(paragraphs) > 0 and any(is_txt(p) for p in paragraphs)
        return False

    @lru_cache(maxsize=1)
    def extract_bibtex_citations(self):
        parser = BibTexParser(customization=convert_to_unicode)
        bib_database = bibtexparser.loads(self.raw_content, parser=parser)
        return [BibtexCitation(bib) for bib in bib_database.entries]

    @lru_cache(maxsize=1)
    def extract_apa_citations(self):
        # Pattern about "how a markdown document with APA citation" should be:
        pattern = match(Document) % {  # it should be an instance of Document
            "children+>content": (  # where somewhere in the content of it's children
                regex(APA_REGEXP)  # a line matches the general APA regex
                >> "raw_apa_match"
                # and we store the results of the regex matcher in the "raw_apa_match" variable
            )
        }
        result = pattern.match(self.content)
        if result.is_match:
            return [
                APACitation(m.groupdict())
                for m in (r["raw_apa_match"] for r in result.bindings)
            ]
        return []

    def detect_doi_citations(self):
        pattern = match(Document) % {
            "children+>content": regex(
                r"(http.*|doi\.org.*)?(10.(\d)+/([^(\s\>\"\<)])+)"
            )
            @ "doi_url"
        }
        result = pattern.match(self.content)
        if result.is_match:
            urls = []
            for doi_url in (r["doi_url"] for r in result.bindings):
                doi_url = (
                    doi_url.replace("https://", "")
                    .replace("http://", "")
                    .replace("doi.org/", "")
                )
                urls.append(doi_url)
            return urls
        return []

    @lru_cache(maxsize=1)
    def extract_citations_from_doi(self):
        doi_urls = self.detect_doi_citations()
        if not doi_urls:
            return []
        bibtex_lib = ""
        for doi_url in self.detect_doi_citations():
            # url = f"https://doi.org/{doi_url}"
            # header = {
            #     "Accept": "application/x-bibtex",
            # }
            # response = requests.get(url, headers=header)
            # bibtex = response.text
            url = f"https://citation.crosscite.org/format?doi={doi_url}&style=bibtex&lang=en-US"
            response = requests.get(url)
            bibtex = response.text
            bibtex_lib += f"\n{bibtex}"
        parser = BibTexParser(customization=convert_to_unicode)
        bib_database = bibtexparser.loads(bibtex_lib, parser=parser)
        return [BibtexCitation(bib) for bib in bib_database.entries]

    @property
    def has_bibtex_citations(self):
        return self.extract_bibtex_citations() != []

    @property
    def has_apa_citations(self):
        return self.extract_apa_citations() != []

    @property
    def has_doi(self):
        return self.extract_citations_from_doi() != []

    @property
    def has_citations(self):
        return self.has_bibtex_citations or self.has_doi or self.has_apa_citations

    def extract_citations(self):
        if self.has_bibtex_citations:
            return self.extract_bibtex_citations()
        if self.has_doi:
            return self.extract_citations_from_doi()
        return self.extract_apa_citations()
