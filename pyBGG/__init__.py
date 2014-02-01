#!/usr/bin/python
# coding: utf-8

"""
BoardGameGeek XML API for Python

Copyright © 2012 Francesco Gigli <jaramir@gmail.com>

pyBGG is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

pyBGG is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with pyBGG.  If not, see <http://www.gnu.org/licenses/>.

"""

import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import xml.etree.ElementTree as ET

root = "http://www.boardgamegeek.com/xmlapi/"

boardgame_cache = {}

class BoardGame(object):
    def __init__(self, et, fetched=False):
        self.et = et
        self.id = et.attrib["objectid"]
        self.fetched = fetched

    def __getattr__(self, name):
        el = self.__find(name)
        if el is None:
            raise AttributeError(name)
        return el.text

    def __fetch(self):
        if self.fetched:
            return

        if self.id not in boardgame_cache:
            url = root + "boardgame/" + urllib.parse.quote(self.id)
            tree = ET.parse(urllib.request.urlopen(url))
            boardgame_cache[self.id] = tree.find("boardgame")
        self.et = boardgame_cache[self.id]

        self.fetched = True

    def __find(self, name):
        el = self.et.find(name)
        if el is None:
            self.__fetch()
            el = self.et.find(name)
        return el

    def __findall(self, term):
        names = self.et.findall(term)
        if not names:
            self.__fetch()
            names = self.et.findall(term)
        return names

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    @classmethod
    def by_id(cls, id):
        """
        Creates a BoardGame instance given an objectid (accessible via the id attribute).

        """
        et = ET.fromstring('<boardgame objectid="%s"/>' % id)
        return cls(et)

    @property
    def name(self):
        """
        Returns the first name.
        Prefear primary names.

        """
        names = self.__findall("name")

        # sort by sortindex if available
        names.sort(key=lambda e: e.attrib.get("sortindex", "1"))

        # find a primary one
        for name in names:
            if "primary" in name.attrib:
                return name.text

        # return the first
        return names[0].text

    @property
    def names(self):
        """
        Returns all names sorted by sortindex (popularity, I suppose).

        """
        self.__fetch() # requires full info
        names = self.__findall("name")
        names.sort(key= lambda e: e.attrib["sortindex"])
        return [ n.text for n in names ]

    @property
    def thumbnail(self):
        """
        Returns the thumbnail.

        """
        self.__fetch() # requires full info
        thumbnail = self.et.find("thumbnail")
        if thumbnail is not None:
            return thumbnail.text
        return None

    @property
    def image(self):
        """
        Returns the image.

        """
        self.__fetch() # requires full info
        image = self.et.find("image")
        if image is not None:
            return image.text
        return None

def search(term, exact=False, prefetch=False):
    """
    Search for games by name and by AKAs and return a list of BoardGames

    term: name to look for
    exact: do a search for the exact term and return one BoardGame or None
    prefetch: if set to True fetch game info for all results with a single call

    """

    url = root + "search?search=" + urllib.parse.quote(term)
    if exact:
        url += "&exact=1"

    tree = ET.parse(urllib.request.urlopen(url))

    games = tree.findall("boardgame")

    if prefetch:
        games = __prefetch([ urllib.parse.quote(el.attrib["objectid"]) for el in games ])

    rv = []
    for bg in games:
        rv.append(BoardGame(bg, fetched=prefetch))

    if exact:
        if rv:
            return rv[0]
        return None
    return rv

def collection(username, own=False, prefetch=False):
    """
    Retrieve games in a user's collection.

    username: the BGG username (eg. "cesco")
    owned: if set to True return only owned games
    prefetch: if set to True fetch game info for all results with a single call

    """

    url = root + "collection/" + urllib.parse.quote(username)
    if own:
        url += "?own=1"

    return __fetch_games(url, prefetch)

def geeklist(list_id, prefetch=False):
    """
    Retrieve all boardgames contained into a GeekList

    """
    url = root + "geeklist/" + urllib.parse.quote(list_id)

    return __fetch_games(url, prefetch)

def __fetch_games(url, prefetch=False):
    tree = ET.parse(urllib.request.urlopen(url))

    games = tree.findall("item[@objecttype='thing'][@subtype='boardgame']")

    if prefetch:
        games = __prefetch([ urllib.parse.quote(el.attrib["objectid"]) for el in games ])

    rv = []
    for bg in games:
        rv.append(BoardGame(bg, fetched=prefetch))
    return rv

def __prefetch(ids):
    """
    Fetch and push in boardgame_cache full info for all boardgames ids passed

    """
    murl = root + "boardgame/" + ",".join(ids)
    mtree = ET.parse(urllib.request.urlopen(murl))
    for subtree in mtree.findall("boardgame"):
        boardgame_cache[subtree.attrib["objectid"]] = subtree
        yield subtree
