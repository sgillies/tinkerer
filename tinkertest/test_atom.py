'''
    Atom Generator Test
    ~~~~~~~~~~~~~~~~~~~

    Tests the Atom feed generator.

    :copyright: Copyright 2011-2013 by Vlad Riscutia and contributors (see
    CONTRIBUTORS file)
    :license: FreeBSD, see LICENSE file
'''
import datetime
import email.utils
import os
from tinkerer import paths, post
from tinkertest import utils
import time
from xml.etree import ElementTree as ET


# get expected pubdate based on date
def expected_pubdate(year, month, day):
    return datetime.date(year, month, day).isoformat()


# test case
class TestAtom(utils.BaseTinkererTest):
    def test_atom(self):
        # create some posts
        for new_post in [
                ("Post 1",
                    datetime.date(2010, 10, 1),
                    "Lorem ipsum",
                    "category 1"),
                ("Post 2",
                    datetime.date(2010, 11, 2),
                    "dolor sit",
                    "category 2"),
                ("Post 3",
                    datetime.date(2010, 12, 3),
                    "amet, consectetuer",
                    "category 3")]:
            post.create(new_post[0], new_post[1]).write(
                    content=new_post[2],
                    categories=new_post[3])

        self.build()

        feed_path = os.path.join(paths.html, "atom.html")

        # check feed was created
        self.assertTrue(os.path.exists(feed_path))

        feed = ET.parse(feed_path).getroot()

        self.assertEquals(
            "My blog", 
            feed.find('{http://www.w3.org/2005/Atom}title').text)
        self.assertEquals(
            "Post 1",
            feed.findall(
                '{http://www.w3.org/2005/Atom}entry')[2].find(
                    '{http://www.w3.org/2005/Atom}title').text)
