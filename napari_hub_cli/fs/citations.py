# General APA named regex
import re
from contextlib import suppress

APA_REGEXP = re.compile(
    r"^(?=\w)"  # The apa reference has to start by an alphanum symbol
    r"(?P<author>[^(]+)"  # starts by the authors
    r" \((?P<year>\d+)\)"  # followed by the date between brackets
    r"\.\s+"  # finishing with a dot and a space
    r"(?P<title>[^(.[]+)"  # followed by the title of the paper (all chars until we reach a '(' or  a '.')
    r"(?P<edition>\([^)]+\))?"  # optionnaly, an edition could be there (all chars between "()" after the title)
    r"(\s+\[(?P<additional>[^]]+)+\])?"  # optionaly, additional information (all chars between "[]") after the title
    r"\.\s+"  # following the title and the optional edition number, there's a dot
    r"(?P<journal>(.(?!, [\d(]))+.)"  # followed by the journal/publisher (a char that is not followed by a comma with a number or a parenthesis)
    r"(, (?P<volume>[^,.]+))?"  # followed by an optional number of volume
    r"(, (?P<pages>[^ ,.]+))?"  # followed by an optional number of page
    # r"([ ,.]+http(s)?://(?P<url>[^ ]+))?"  # followed by an optional location url
    # r"((?=[ ,.]http(s)?://)[ ,.]+(http(s)?://)(doi\.org/)(?P<doi>[^ ]+))?"  # followed by an optional DOI (non DOI location url not supported)
    r"([ ,.]+(?P<doi>[^ ]+))?"  # OR followed by an optional DOI
    r"( \((?P<retraction>[^)]+)\))?"  # folloawed by an optional retraction
)


class Citation(object):
    required_fields = []

    def __init__(self, data):
        self.data = data

    def __getattr__(self, key):
        return self.data[key]

    def as_dict(self):
        d = {}
        for field, _type in self.required_fields:
            with suppress(KeyError):
                value = getattr(self, field)
                if value is None:
                    continue
                try:
                    d[field] = _type(value)
                except Exception:
                    d[field] = value
        return d

    @property
    def type(self):
        return "article"

    @property
    def doi(self):
        return self.data["doi"].replace("https://", "").replace("doi.org/", "")


class BibtexCitation(Citation):
    required_fields = [
        ("authors", list),
        ("title", str),
        ("year", int),
        ("url", str),
        ("doi", str),
        ("publisher", str),
        ("journal", str),
        ("volume", int),
        ("pages", int),
        ("issue", int),
        ("type", str),
    ]

    @property
    def authors(self):
        authors_split = [a.strip().split(",") for a in self.author.split(" and ")]
        authors = []
        for family_names, *given_names in authors_split:
            if given_names:
                authors.append(
                    {
                        "family-names": family_names.strip(),
                        "given-names": given_names[0].strip(),
                    }
                )
            else:
                authors.append(
                    {
                        "given-names": family_names.strip(),
                    }
                )
        return authors


class APACitation(Citation):
    required_fields = [
        ("authors", list),
        ("title", str),
        ("year", int),
        ("doi", str),
        ("journal", str),
        ("volume", int),
        ("pages", int),
        ("type", str),
    ]

    @property
    def authors(self):
        authors_and = self.author.split(" and ")
        authors_and = ", ".join(authors_and)
        authors_split = [a.strip() for a in authors_and.split(",")]
        authors = []
        for family_names, given_names in zip(authors_split[::2], authors_split[1::2]):
            authors.append(
                {
                    "family-names": family_names,
                    "given-names": given_names,
                }
            )
        return authors
