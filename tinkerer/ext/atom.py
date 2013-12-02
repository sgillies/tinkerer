'''
    atom
    ~~~~

    Atom feed extension.

    :copyright: Copyright 2011-2013 by Vlad Riscutia and contributors (see
    CONTRIBUTORS file)
    :license: FreeBSD, see LICENSE file
'''
import cgi
import email.utils
import time
from urlparse import urlparse

from sphinx.util.compat import Directive
from tinkerer import __version__ as tinkerer_version
from tinkerer.ext import patch

class SummaryDirective(Directive):
    '''
    Optional summary metadata for posts and pages.

    From http://tools.ietf.org/html/rfc4287#section-4.2.13:

      The "atom:summary" element is a Text construct that conveys a
      short summary, abstract, or excerpt of an entry.

      It is not advisable for the atom:summary element to duplicate
      atom:title or atom:content because Atom Processors might assume
      there is a useful summary when there is none.

    The directive is not rendered, just stored in the 
    metadata and passed to the templating engine.
    '''
    required_arguments = 0
    optional_arguments = 100
    has_content = False

    def run(self):
        '''
        Called when parsing the document.
        '''
        env = self.state.document.settings.env

        # store author in metadata
        summary = " ".join(self.arguments)
        env.blog_metadata[env.docname].summary = summary

        return []

def add_atom(app, context):
    '''
    Adds RSS service link to page context.
    '''
    context["rights"] = app.config.rights
    context["use_atom_feed"] = app.config.use_atom_feed


def generate_feed(app):
    '''
    Generates Atom feed.
    '''
    env = app.builder.env
 
    # don't do anything if no posts are available
    if not env.blog_posts:
        return

    context = dict()
    
    # Some parts of the tag: URI to be used for ids.
    parts = urlparse(app.config.website)
    netloc = parts.netloc
    idpath = parts.path.strip('/').replace("/", ":")

    # feed items
    context["entries"] = []
    for post in env.blog_posts:
        link = "%s%s.html" % (app.config.website, post)

        timestamp = env.blog_metadata[post].date.isoformat()
        entry_date = timestamp.split('T')[0]

        categories = [
            category[1] for category in 
            ( env.blog_metadata[post].filing["categories"]
              + env.blog_metadata[post].filing["tags"])]

        context["entries"].append({
            "title": env.titles[post].astext(),
            "id": "tag:%s,%s:%s:%s" % (
                netloc, entry_date, idpath, post[11:]),
            "link": link,
            "summary": getattr(env.blog_metadata[post], 'summary', None),
            "categories": categories, # terms
            "published": timestamp,
            "author": env.blog_metadata[post].author,
            "content": env.blog_metadata[post].body,
        })

    # feed metadata 
    context["title"] = app.config.project
    context["id"] = "tag:%s,%s:%s" % (
        netloc, app.config.blog_date, idpath)
    context["link"] = app.config.website
    context["subtitle"] = app.config.tagline
    context["language"] = "en-us"
    context["rights"] = app.config.copyright
    context["tinkerer_version"] = tinkerer_version
  
    # feed pubDate is equal to latest post pubDate
    context["updated"] = context["entries"][0]["published"]
    
    yield ("atom", context, "atom.xml")


