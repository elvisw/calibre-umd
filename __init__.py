#!/usr/bin/env  python
__license__   = 'GPL v3'
__copyright__ = '2011, Thihy <my2003cat@gmail.com>'
__docformat__ = 'restructuredtext en'


import os
from calibre.customize import MetadataReaderPlugin
from calibre_plugins.umd_metadata_reader.umdfile import UMDFile
from calibre_plugins.umd_metadata_reader.plugininfo import PLUGIN_VERSION
from calibre_plugins.umd_metadata_reader.utilities import debug_print
from calibre.ebooks.metadata import MetaInformation
from calibre.utils.logging import default_log

class UmdMetadata(MetadataReaderPlugin):
  
  name        = 'UMD Metadata Reader'
  author      = 'Thihy'
  description = 'Read UMD metadata'
  file_types  = set(['umd'])
  version     = PLUGIN_VERSION
  
  options = set([
  ])
  
  def initialize(self):
      #import calibre.constants
      #calibre.constants.DEBUG=True
      pass
  
  def get_metadata(self,stream, ftype):
    debug_print("Parsing UMD file...")
    mi = MetaInformation(None,None)
    umdFile = UMDFile()
    umdFile.read(stream) # try error
    debug_print("Read meta data ...")
    debug_print("UMD title:%s,authors:%s" % (umdFile.Title,umdFile.Author));
    if umdFile.Title:
        mi.title = umdFile.Title
    if umdFile.Author:
        mi.authors = [umdFile.Author];
    if umdFile.Publisher:
        mi.publisher = umdFile.Publisher;
    else:
        mi.publisher="Thihy";
    if umdFile.PublishDate:
        mi.pubdate = umdFile.PublishDate;
    if umdFile.Cover:
        cover=umdFile.Cover
        mi.cover_data = ('jpg',umdFile.CoverData);
    debug_print("Read meta data[DONE], title:%s,authors:%s" % (mi.title,mi.authors))
    return mi
  