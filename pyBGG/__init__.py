#!/usr/bin/python
# coding: utf-8

""" BoardGameGeek XML API for Python

Copyright (c) 2012 Francesco Gigli

http://boardgamegeek.com/xmlapi/termsofuse
http://boardgamegeek.com/wiki/page/BGG_XML_API
http://boardgamegeek.com/wiki/page/BGG_XML_API2
"""

import urllib
import urllib2
import xml.etree.ElementTree as ET

root = "http://www.boardgamegeek.com/xmlapi/"

def search( term, exact=False ):
    """ Search for games by name and by AKAs
    
    >>> search( '1830' ) # doctest:+ELLIPSIS
    [...{'id': '421', 'name': '1830: Railways & Robber Barons'}...]

    >>> search( '1830', True ) # returns None

    >>> search( '1830: Railways & Robber Barons', True )
    {'id': '421', 'name': '1830: Railways & Robber Barons'}

    """

    url = root + "search?search=" + urllib.quote( term )
    if exact:
        url += "&exact=1"

    tree = ET.parse( urllib2.urlopen( url ) )

    rv = []
    for bg in tree.findall( "boardgame" ):
        rv.append( {
            "id": bg.attrib["objectid"],
            "name": bg.find( "name" ).text,
            } )

    if exact:
        if rv:
            return rv[0]
        return None
    return rv

def boardgame( id ):
    """ Retrieve information about a particular game or games

    >>> boardgame( "421" ) # doctest:+ELLIPSIS
    {...'description': "1830 is one of the most famous 18xx games...}

    """

    url = root + "boardgame/" + urllib.quote( id )

    tree = ET.parse( urllib2.urlopen( url ) )
    
    bg = tree.find( "boardgame" )

    rv = {
        "id": bg.attrib["objectid"],
        "description": bg.find( "description" ).text,
        "thumbnail": bg.find( "thumbnail" ).text,
        "image": bg.find( "image" ).text,
        }
    
    return rv

def wishlist( username ):
    """ Retrieve games in a user's wishlist

    >>> wishlist( "cesco" ) # doctest:+ELLIPSIS
    [...{'id': '421', 'name': '1830: Railways & Robber Barons'}...]
    
    """
    
    url = root + "collection/" + urllib.quote( username ) + "?wishlist=1"

    tree = ET.parse( urllib2.urlopen( url ) )

    rv = []
    for bg in tree.findall( "item" ):
        rv.append( {
                "id": bg.attrib["objectid"],
                "name": bg.find( "name" ).text,
                } )

    return rv

def getTestSuite():
    import unittest
    import doctest
    suite = unittest.TestSuite()
    suite.addTest( doctest.DocTestSuite( __name__ ) )
    return suite

if __name__ == "__main__":
    import unittest
    runner = unittest.TextTestRunner()
    runner.run( getTestSuite() )
