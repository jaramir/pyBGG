#!/usr/bin/python
# coding: utf-8

"""
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
import urllib2
import StringIO
import unittest
import pyBGG

# mock BGG server

canned_response = {
    "http://www.boardgamegeek.com/xmlapi/boardgame/13": open( "fixture/bgCatan" ).read(),
    "http://www.boardgamegeek.com/xmlapi/boardgame/421": open( "fixture/bg1830" ).read(),
    "http://www.boardgamegeek.com/xmlapi/boardgame/66000,68448,31260,43018,2346,58110,2452,34010,60054,24480,19764,8192,20551,40692,57072,57070,71818,27627,34127,20426,11955,28025": open( "fixture/bgMulti" ).read(),
    "http://www.boardgamegeek.com/xmlapi/search?search=1830%3A%20Railways%20%26%20Robber%20Barons": open( "fixture/search1830name" ).read(),
    "http://www.boardgamegeek.com/xmlapi/search?search=I%20Coloni%20di%20Catan&exact=1": open( "fixture/searchCatan" ).read(),
    "http://www.boardgamegeek.com/xmlapi/search?search=pyBGG%20test%20search&exact=1": open( "fixture/searchTest" ).read(),
    "http://www.boardgamegeek.com/xmlapi/collection/cesco": open( "fixture/collectionCesco" ).read(),
    "http://www.boardgamegeek.com/xmlapi/collection/cesco?own=1": open( "fixture/collectionCescoOwn" ).read(),
    "http://www.boardgamegeek.com/xmlapi/search?search=1830": open( "fixture/search1830" ).read(),
    "http://www.boardgamegeek.com/xmlapi/boardgame/88400,37322,31013,111775,421,31230,56839,56841,56840,59644,59645,23189,70875,2396": open( "fixture/bgMulti1830" ).read(),
}

class TestResponse( object ):
    def __init__( self, request ):
        url = request.get_full_url()
        if not url in canned_response:
            raise Exception( "%s not in canned response!" % url )
        self.request = request
        self.code = 200
        self.msg = "OK"
        self.content = StringIO.StringIO( canned_response[url] )
        self.read = self.content.read

    def info( self ):
        return []

class TestHandler( urllib2.HTTPHandler ):
    def __init__( self ):
        self.hits = []

    def http_open( self, req ):
        self.hits.append( req.get_full_url() )
        return TestResponse( req )

    def reset_hits( self ):
        self.hits = []

handler = TestHandler()
opener = urllib2.build_opener( handler )
urllib2.install_opener( opener )

## This works but will make a request per fixture on every run
## Uncomment and use when necessary
##
##class fixtureTest( unittest.TestCase ):
##    def test_fixtures( self ):
##        for url in canned_response.keys():
##            req = urllib2.Request( url )
##            op = urllib2.build_opener( urllib2.HTTPHandler )
##            self.assertEqual( op.open( req ).read(), opener.open( req ).read() )

class handlerTest( unittest.TestCase ):
    def setUp( self ):
        handler.reset_hits()

    def test_count_hits( self ):
        url = "http://www.boardgamegeek.com/xmlapi/boardgame/13"
        urllib2.urlopen( url ).read()
        self.assertEqual( handler.hits, [url] )

class pyBGGTest( unittest.TestCase ):

    def setUp( self ):
        handler.reset_hits()

    def test_exact_search_gone_wrong( self ):
        bg = pyBGG.search( "pyBGG test search", exact=1 )
        self.assertEqual( None, bg )

    def test_exact_search( self ):
        bg = pyBGG.search( "I Coloni di Catan", exact=1 )
        self.assertEqual( "13", bg.id )

    def test_name_in_search( self ):
        resp = pyBGG.search( "1830: Railways & Robber Barons" )
        self.assertIn( "1830", resp[0].name )

    def test_description_in_search( self ):
        resp = pyBGG.search( "1830: Railways & Robber Barons" )
        self.assertIn( "1830 is one of the most famous 18xx games", resp[0].description )

    def test_boardgame_by_id( self ):
        bg = pyBGG.BoardGame.by_id( "421" )
        self.assertEqual( "1830: Railways & Robber Barons", bg.name )

    def test_boardgame_info_taken_from_memory_cache( self ):
        pyBGG.boardgame_cache = {} # empty cache now
        bg = pyBGG.BoardGame.by_id( "421" )
        bg.description
        bg2 = pyBGG.BoardGame.by_id( "421" )
        bg2.names
        self.assertEqual( handler.hits, [ "http://www.boardgamegeek.com/xmlapi/boardgame/421" ] )

    def test_game_with_many_sorted_names( self ):
        en = "The Settlers of Catan"
        us = "Catan"
        it = "I Coloni di Catan"
        ru = u"Заселниците на Катан"
        ja = u"カタンの開拓者"

        bg = pyBGG.BoardGame.by_id( "13" )
        names = bg.names

        self.assertIsInstance( names, list )

        self.assertIn( en, names ) # sort = 5
        self.assertIn( us, names ) # sort = 1
        self.assertIn( it, names ) # sort = 3
        self.assertIn( ru, names ) # sort = 1
        self.assertIn( ja, names ) # sort = 1

        self.assertLess( names.index( ru ), names.index( it ), "Wrong sort: %s before %s" % ( it, ru ) )
        self.assertLess( names.index( it ), names.index( en ), "Wrong sort: %s before %s" % ( en, it ) )

    def test_game_names_from_search( self ):
        bg = pyBGG.search( "I Coloni di Catan", exact=1 )
        self.assertIn( "The Settlers of Catan", bg.names )
        self.assertIn( "I Coloni di Catan", bg.names )

    def test_search_does_prefetch( self ):
        handler.reset_hits()
        games = pyBGG.search( "1830", prefetch=True )
        hits = [
            "http://www.boardgamegeek.com/xmlapi/search?search=1830",
            "http://www.boardgamegeek.com/xmlapi/boardgame/88400,37322,31013,111775,421,31230,56839,56841,56840,59644,59645,23189,70875,2396",
            ]
        self.assertListEqual( handler.hits, hits )

    def test_collection( self ):
        coll = pyBGG.collection( "cesco" )
        self.assertIsInstance( coll, list )
        self.assertIsInstance( coll[0], pyBGG.BoardGame )
        self.assertIn( pyBGG.BoardGame.by_id( "57070" ), coll )

    def test_collection_prefetch( self ):
        handler.reset_hits()
        coll = pyBGG.collection( "cesco", own=True, prefetch=True )
        for game in coll:
            game.names # this would normaly generate a hit
        hits = [
            "http://www.boardgamegeek.com/xmlapi/collection/cesco?own=1",
            "http://www.boardgamegeek.com/xmlapi/boardgame/66000,68448,31260,43018,2346,58110,2452,34010,60054,24480,19764,8192,20551,40692,57072,57070,71818,27627,34127,20426,11955,28025",
            ]
        self.assertListEqual( handler.hits, hits )

    def test_prefetch_populates_cache( self ):
        coll = pyBGG.collection( "cesco", own=True, prefetch=True )
        for game in coll:
            self.assertIn( game.id, pyBGG.boardgame_cache.keys() )

if __name__ == '__main__':
    unittest.main()
