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

import urllib
import urllib2
import xml.etree.ElementTree as ET

root = "http://www.boardgamegeek.com/xmlapi/"

class DoubleFetch( Exception ):
    """
    A BoardGame should never ever fetch data two times

    """
    pass

class BoardGame( object ):
    def __init__( self, et ):
        self.et = et
        self.id = et.attrib["objectid"]

    def __getattr__( self, name ):
        el = self.__find( name )
        if el is None:
            raise AttributeError( name )
        return el.text

    def __find( self, name ):
        el = self.et.find( name )
        if el is None:
            self.fetch()
            el = self.et.find( name )
        return el

    def __findall( self, term ):
        names = self.et.findall( term )
        if not names:
            self.fetch()
            names = self.et.findall( term )
        return names

    @classmethod
    def by_id( cls, id ):
        """
        Creates a BoardGame instance given an objectid (accessible via the id attribute).

        """
        et = ET.fromstring( '<boardgame objectid="%s"/>' % id )
        return cls( et )

    @property
    def name( self ):
        """
        Returns the primary name.

        """
        return self.__find( "name[@primary='true']" ).text

    @property
    def names( self ):
        """
        Returns all names sorted by sortindex (popularity, I suppose).

        """
        names = self.__findall( "name" )
        names.sort( key= lambda e: e.attrib["sortindex"] )
        return [ n.text for n in names ]

    def fetch( self ):
        """
        Fetch the complete informations for this game

        should never be called to begin with
        will rise DoubleFetch if called more than one time

        """
        url = root + "boardgame/" + urllib.quote( self.id )
        tree = ET.parse( urllib2.urlopen( url ) )
        self.et = tree.find( "boardgame" )

        # never ever call me again
        def raise_df():
            raise DoubleFetch()
        self.fetch = raise_df

def search( term, exact=False ):
    """
    Search for games by name and by AKAs and return a list of BoardGames

    term: name to look for
    exact: do a search for the exact term and return one BoardGame or None

    """

    url = root + "search?search=" + urllib.quote( term )
    if exact:
        url += "&exact=1"

    tree = ET.parse( urllib2.urlopen( url ) )

    rv = []
    for bg in tree.findall( "boardgame" ):
        rv.append( BoardGame( bg ) )

    if exact:
        if rv:
            return rv[0]
        return None
    return rv
