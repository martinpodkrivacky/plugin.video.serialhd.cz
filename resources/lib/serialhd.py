#/* coding: UTF-8 bez BOM
#/*
# *      Copyright (C) 2017 Martin Podkrivacky
# *
# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with this program; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# *
# */

import re,os,urllib,urllib2,shutil,traceback,cookielib,HTMLParser
import util,resolver
import hashlib
import json
from urllib import quote_plus
from provider import ContentProvider, cached

HDRS = {"User-Agent": "SerialHDKodi"}

class serialhdContentProvider(ContentProvider):

    def __init__(self,username=None,password=None,filter=None):
        ContentProvider.__init__(self,'serialhd.cz','http://kodi.serialhd.cz/final',username,password,filter)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar()))
        urllib2.install_opener(opener)
        self.order_by = ''

    def capabilities(self):
        return ['categories','resolve','search']

    def search(self,keyword):
        m = hashlib.md5()
        m.update(self.loginpassword)
        keyword = urllib.quote_plus(keyword)
        return self.load_json_items(util.request(self._url('listings.php?type=search&q='+keyword)))

    def list(self,url):
        if url.find('#listitems#') == 0:
            url = url[11:]
            return self.load_json_items(util.request(self._url(url)))
        if url.find('#jsonlist#') == 0:
            url = url[10:]
            return self.load_json_items(util.request(self._url(url)))
        return self.load_json_items(util.request(self._url(url)))
	
    def categories(self):
        return self.load_json_items(util.request(self._url('hlavniMenuDoplnekKombinovany.json')))

    def load_json_items(self,page):
        m = hashlib.md5()
        m.update(self.loginpassword)
        result = []
        page = page.replace("YOURUSERNAME", self.loginusername)
        page = page.replace("YOURPASSWORD", m.hexdigest())
        json_video_array = json.loads(page)
        for item_properties in json_video_array:
            if item_properties['type'] == 'video':
				item = self.video_item()
				item['title'] = item_properties['title']
				item['genre'] = item_properties['genre']
				item['fileextension'] = item_properties['fileextension']
				item['img'] = item_properties['img']
				item['fanart'] = item_properties['backdrop']
				item['codec'] = item_properties['codec']
				item['url'] = item_properties['url']
				item['lang'] = item_properties['lang']
				item['quality'] = item_properties['quality']
				item['plot'] = item_properties['plot']
				item['year'] = int(item_properties['year'])
            else:
				item = self.dir_item()
				item['title'] = item_properties['title']
				item['url'] = item_properties['url']
				if 'img' in item_properties and item_properties['img'] is not None:
					item['img'] = item_properties['img']
				if 'plot' in item_properties and item_properties['plot'] is not None:
					item['plot'] = item_properties['plot']
				if 'year' in item_properties and item_properties['year'] is not None:
					item['year'] = int(item_properties['year'])
            result.append(item)
        return result

    def resolve(self,item,captcha_cb=None,select_cb=None):
        item = item.copy()
        data = util.request(self._url(item['url']))	
        data = util.substr(data,'[',']')
        result = self.findstreams(data,['{"url":"(?P<url>[^"]*?)"}'])
        return result[0]