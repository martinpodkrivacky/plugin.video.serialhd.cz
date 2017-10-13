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
from urllib import quote_plus
from provider import ContentProvider, cached

HDRS = {"User-Agent": "SerialHDKodi"}

class serialhdContentProvider(ContentProvider):

    def __init__(self,username=None,password=None,filter=None):
        ContentProvider.__init__(self,'serialhd.cz','https://kodi.serialhd.cz/096',username,password,filter)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar()))
        urllib2.install_opener(opener)
        self.order_by = ''

    def capabilities(self):
        return ['categories','resolve','search']

    def search(self,keyword):
        keyword = urllib.quote_plus(keyword)
        return self.list_serialy(util.request(self._url('serialy_search.php?q='+keyword)))

    def list(self,url):
        if url.find('#cat#') == 0:
            url = url[5:]
            return self._categories(util.request(self._url(url)),'yes')
        if url.find('#epizody#') == 0:
            url = url[9:]
            return self.video_epizody(util.request(self._url(url)),url)
        if url.find('#serie#') == 0:
            url = url[7:]
            return self.video_serie(util.request(self._url(url)))
        if url.find('#show#') == 0:
            url = url[6:]
            return self.list_serialy(util.request(self._url(url)))
        if url.find('#vsechnyserialy#') == 0:
            return self.categories_vsechnyserialy()
        if url.find('#filtrovatserialy#') == 0:
            return self.categories_filtrovatserialy()
        if url.find('#ostatnezoradenie#') == 0:
            return self.categories_ostatnezoradenie()
        return self.list_serialy(util.request(self._url(url)))
	
    def categories(self):
        result = []
        item = self.dir_item()
        item['title'] = 'Všechny seriály'
        item['url'] = '#vsechnyserialy#'
        result.append(item)
        item = self.dir_item()
        item['title'] = 'Filtrovat seriály'
        item['url'] = '#filtrovatserialy#'
        result.append(item)
        item = self.dir_item()
        item['title'] = 'Ostatní seřazení'
        item['url'] = '#ostatnezoradenie#'
        result.append(item)
        return result
	
    def categories_vsechnyserialy(self):
        result = []
        item = self.dir_item()
        item['title'] = 'Seřazené abecedně'
        item['url'] = '#show#serialy_abecedne.php'
        result.append(item)
        item = self.dir_item()
        item['title'] = 'Nejsledovanější'
        item['url'] = '#show#serialy_nejsledovanejsi.php'
        result.append(item)
        item = self.dir_item()
        item['title'] = 'Podle hodnocení'
        item['url'] = '#show#serialy_hodnoceni.php'
        result.append(item)
        item = self.dir_item()
        item['title'] = 'Poslední přidané'
        item['url'] = '#show#serialy_posledneserialy.php'
        result.append(item)
        return result
	
    def categories_filtrovatserialy(self):
        result = []
        item = self.dir_item()
        item['title'] = 'Podle žánru'
        item['url'] = '#cat#serialy_zanre.php'
        result.append(item)
        item = self.dir_item()
        item['title'] = 'Podle roku'
        item['url'] = '#cat#serialy_roky.php'
        result.append(item)
        item = self.dir_item()
        item['title'] = 'Podle začátečního písmena'
        item['url'] = '#cat#serialy_pismena.php'
        result.append(item)
        return result
	
    def categories_ostatnezoradenie(self):
        result = []
        item = self.dir_item()
        item['title'] = 'Zobrazit poslední přidané epizody'
        item['url'] = '#epizody#serialy_posledneepizody.php'
        result.append(item)
        return result

    def video_serie(self,page):
        data = util.substr(page,'----start----','----end----')
        result = []
        for m in re.finditer('----startserial---->>>URL:(?P<url>[^"]*?)>>>NAME:(?P<name>[^"]*?)----endserial----',data,re.IGNORECASE|re.DOTALL):
            item = self.dir_item()
            item['url'] = '#epizody#' + m.group('url')
            item['title'] = m.group('name')
            self._filter(result,item)
        return result

    def video_epizody(self,page,url):
		result = []
		page = util.substr(page,'----start----','----end----')
		for m in re.finditer('----startserial---->>>URL:(?P<url>[^"]*?)>>>NAME:(?P<name>[^"]*?)>>>YEAR:(?P<year>[^"]*?)>>>INFO:(?P<plot>[^"]*?)>>>SERIE:(?P<season>[^"]*?)>>>SUBS:(?P<subs>[^"]*?)>>>EPIZODA:(?P<episode>[^"]*?)>>>IMG:(?P<img>[^"]*?)----endserial----',page,re.IGNORECASE|re.DOTALL):
			item = self.video_item()
			item['title'] = m.group('name')
			item['season'] = m.group('season')
			item['episode'] = m.group('episode')
			item['plot'] = m.group('plot')
			item['img'] = self._url(m.group('img'))
			item['subs'] = self._url(m.group('subs'))
			item['url'] = self._url(m.group('url'))
			if self.strict_search:
				item['year'] = m.group('year')
			result.append(item)
		return result

    def list_serialy(self,page):
        page = util.substr(page,'----start----','----end----')
        result = []
        for m in re.finditer('----startserial---->>>URL:(?P<url>[^"]*?)>>>NAME:(?P<name>[^"]*?)>>>INFO:(?P<plot>[^"]*?)>>>IMG:(?P<img>[^"]*?)----endserial----',page,re.IGNORECASE|re.DOTALL):
            item = self.dir_item()
            item['url'] = '#serie#' + m.group('url')
            item['img'] = self._url(m.group('img'))
            item['plot'] = m.group('plot')
            item['title'] = m.group('name')
            self._filter(result,item)
        return result

    @cached()
    def _categories(self,data,pistala):
        data = util.substr(data,'----start----','----end----')
        result = []
        for m in re.finditer('----startserial---->>>URL:(?P<url>[^"]*?)>>>NAME:(?P<name>[^"]*?)----endserial----',data,re.IGNORECASE|re.DOTALL):
            item = self.dir_item()
            item['url'] = '#show#' + m.group('url')
            item['title'] = m.group('name')
            self._filter(result,item)
        return result

    def resolve(self,item,captcha_cb=None,select_cb=None):
        item = item.copy()
        url = self._url(item['url'])
        data = util.request(self._url(item['url']))	
        data = util.substr(data,'----start----','----end----')
        result = self.findstreams(data,['----startserial---->>>VIDEO:(?P<url>[^"]*?)>>>TITULKY:(?P<subs>[^"]*?)----endserial----'])
        if len(result)==1:
            return result[0]
        elif len(result) > 1 and select_cb:
            return result[0]
