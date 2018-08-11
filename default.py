# -*- coding: UTF-8 -*-
#/*
# *      Copyright (C) 2013 Libor Zoubek
# *
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
import os
sys.path.append( os.path.join ( os.path.dirname(__file__),'resources','lib') )
import serialhd
import xbmcprovider,xbmcaddon,xbmcutil,xbmc,utmain
import util
import traceback,urllib2

__scriptid__   = 'plugin.video.serialhdfilm.cz'
__scriptname__ = 'SerialHD HDFilm'
__addon__      = xbmcaddon.Addon(id=__scriptid__)
__language__   = __addon__.getLocalizedString
__set          = __addon__.getSetting

settings = {'downloads':__set('downloads'),'quality':__set('quality'),'strict-search':__set('strict-search'),'subs':__set('subs') == 'true'}

params = util.params()
if params=={}:
    xbmcutil.init_usage_reporting( __scriptid__)
provider = serialhd.serialhdContentProvider()
provider.strict_search = __addon__.getSetting('strict-search') == 'true'
provider.loginusername = __addon__.getSetting('username')
provider.loginpassword = __addon__.getSetting('password')

class serialhdXBMContentProvider(xbmcprovider.XBMCMultiResolverContentProvider):

    def resolve(self,url):
        result = xbmcprovider.XBMCMultiResolverContentProvider.resolve(self,url)
        if result:
            # ping serialhd.cz GA account
            host = 'serialhd.cz'
            tc = 'UA-82388941-8'
            try:
                utmain.main({'id':__scriptid__,'host':host,'tc':tc,'action':url})
            except:
                print 'Error sending ping to GA'
                traceback.print_exc()
        return result

serialhdXBMContentProvider(provider,settings,__addon__).run(params)
