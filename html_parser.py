from __future__ import annotations

from bs4 import BeautifulSoup, PageElement
from typing import List, TypedDict


class HTMLParser(object):
    def __init__(self):
        self._soup = None

    def parse(self, html: str):
        self._soup = BeautifulSoup(html, features='lxml')

    def find_all(self, name: str, attrs: TypedDict) -> List[Element]:
        found = self._soup.findAll(name, attrs)
        return [Element(e) for e in found]

    def find_first(self, name: str, attrs: TypedDict) -> Element:
        found = self._soup.find_all(name, attrs)
        assert len(found) > 0
        return Element(found[0])


class Element(object):
    def __init__(self, page_element: PageElement):
        self._page_element = page_element

    def content(self) -> str:
        return self._page_element.string

    def find_all(self, name: str, attrs: TypedDict) -> List[Element]:
        found = self._page_element.find_all(name, attrs)
        return [Element(e) for e in found]

    def find_first(self, name: str, attrs: TypedDict) -> Element:
        found = self._page_element.find_all(name, attrs)
        assert len(found) > 0
        return Element(found[0])
