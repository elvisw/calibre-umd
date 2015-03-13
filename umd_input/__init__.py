#!/usr/bin/env  python
__license__   = 'GPL v3'
__copyright__ = '2011, Thihy <my2003cat@gmail.com>'
__docformat__ = 'restructuredtext en'

'''
Used for UMD input
'''

import os, uuid, re

from calibre.customize.conversion import InputFormatPlugin
from calibre.customize import MetadataReaderPlugin,MetadataWriterPlugin
from calibre_plugins.umd_input.umdfile import UMDFile
from calibre_plugins.umd_input.plugininfo import PLUGIN_VERSION
from calibre.ptempfile import TemporaryDirectory
from calibre.utils.filenames import ascii_filename
from calibre.ebooks.metadata import MetaInformation

HTML_TEMPLATE = u'<html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/><title>%s</title></head><body>\n%s\n</body></html>'

def html_encode(s):
    return s.replace(u'&', u'&amp;').replace(u'<', u'&lt;').replace(u'>', u'&gt;').replace(u'"', u'&quot;').replace(u"'", u'&apos;').replace(u'\n', u'<br/>').replace(u' ', u'&nbsp;')

class UMDInput(InputFormatPlugin):

    name        = 'UMD Input'
    author      = 'Thihy'
    description = 'Convert UMD files to OEB'
    file_types  = set(['umd'])
    version     = PLUGIN_VERSION
    
    options = set([
    ])
    
    def initialize(self):
        from calibre.ebooks import BOOK_EXTENSIONS
        if not 'umd' in BOOK_EXTENSIONS:
            BOOK_EXTENSIONS.append('umd');
        

    def convert(self, stream, options, file_ext, log,
                accelerators):
        from calibre.ebooks.oeb.base import DirContainer
        log.debug("Parsing UMD file...")
        umdFile = UMDFile()
        umdFile.read(stream) # try error
        log.debug("Handle meta data ...")
        from calibre.ebooks.conversion.plumber import create_oebbook
        oeb = create_oebbook(log, None, options,
                encoding=options.input_encoding, populate=False)
        if umdFile.Title:
          oeb.metadata.add('title', umdFile.Title)
        if umdFile.Author:
          oeb.metadata.add('creator', umdFile.Author, attrib={'role':'aut'})
        #oeb.metadata.add('language', d['language'].lower().replace('_', '-'))
        #oeb.metadata.add('generator', d['generator'])
        if umdFile.Publisher:
          oeb.metadata.add('publisher', umdFile.Publisher)

        bookid = str(uuid.uuid4())
        oeb.metadata.add('identifier', bookid, id='uuid_id', scheme='uuid')
        for ident in oeb.metadata.identifier:
            if 'id' in ident.attrib:
                oeb.uid = oeb.metadata.identifier[0]
                break

        with TemporaryDirectory('_umd2oeb', keep=True) as tdir:
            log.debug('Process TOC ...')
            chapters = umdFile.Chapters;
            oeb.container = DirContainer(tdir, log)
            
            
            cover=umdFile.Cover;
            if cover:
                format=cover.format;
                fname='cover.'+format;
                outputFile = os.path.join(tdir, fname);
                cover.save(outputFile);
                id, href = oeb.manifest.generate(id='image',href=ascii_filename(fname))
                oeb.guide.add('cover', 'Cover', href)
            
            if chapters != None:
                i = 1;
                for ch in chapters:
                  chapterTitle = ch.Title
                  chapterContent = ch.Content
                  if chapterTitle is None or chapterContent is None:
                    continue;
                  fname = 'ch_%d.htm' % i
                  outputFile = open(os.path.join(tdir, fname), 'wb')
                  lines = []
                  titleWithoutWhiteSpaces = re.sub(r'\s','',chapterTitle);
                  print "TITLE: %s => %s" % (chapterTitle,titleWithoutWhiteSpaces)
                  chapterContent=chapterContent.replace(u'\u2029','\n');
                  first=True;
                  for line in chapterContent.split('\n'):
                      first = False;
                      print "ADD %s" % line
                      line = line.rstrip();
                      lines.append(u'<p>%s</p>' % html_encode(line))
                      #lines.append(u'<p><img src="%s" /></p>' % html_encode(line.text))
                  outputFile.write((HTML_TEMPLATE % (chapterTitle, u'\n'.join(lines))).encode('utf-8', 'replace'))
                  outputFile.close()
                  oeb.toc.add(chapterTitle, fname)
                  id, href = oeb.manifest.generate(id='html',href=ascii_filename(fname))
                  item = oeb.manifest.add(id, href, 'text/html')
                  item.html_input_href = fname
                  oeb.spine.add(item, True)
                  i = i + 1
        return oeb;