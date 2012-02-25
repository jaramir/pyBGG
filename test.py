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

# mock BGG server
import urllib2
import StringIO

canned_response = {
    "http://www.boardgamegeek.com/xmlapi/boardgame/13": open( "fixture/bgCatan" ).read(),
    "http://www.boardgamegeek.com/xmlapi/boardgame/421": open( "fixture/bg1830" ).read(),
    "http://www.boardgamegeek.com/xmlapi/search?search=1830%3A%20Railways%20%26%20Robber%20Barons": open( "fixture/search1830" ).read(),
    "http://www.boardgamegeek.com/xmlapi/search?search=I%20Coloni%20di%20Catan&exact=1": open( "fixture/searchCatan" ).read(),
    "http://www.boardgamegeek.com/xmlapi/search?search=pyBGG%20test%20search&exact=1": open( "fixture/searchTest" ).read(),
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
    def http_open( self, req ):
        return TestResponse( req )

handler = TestHandler( debuglevel=1 )
opener = urllib2.build_opener( handler )
urllib2.install_opener( opener )

import unittest
import pyBGG

class pyBGGTest( unittest.TestCase ):

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

    def test_raise_on_second_fetch( self ):
        bg = pyBGG.BoardGame.by_id( "421" )
        bg.fetch()
        self.assertRaises( pyBGG.DoubleFetch, bg.fetch )

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

if __name__ == '__main__':
    unittest.main()
