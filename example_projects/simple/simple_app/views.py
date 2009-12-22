from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

from lingcod.manipulators.manipulators import * 
from manipulators import *

from django.conf import settings
from django.utils import simplejson

import models

def simpleManipulators(request, template_name='common/simple-manipulators.html'):
    return render_to_response(template_name, RequestContext(request,{'api_key':settings.GOOGLE_API_KEY}))
  

def testAuth(request):
    print request.session.items()
    from django.contrib.auth import authenticate, login
    print request.COOKIES
    print request.META
    user = authenticate(username='cburt', password='7lobster')
    login(request, user)
    print request.session.items()
    content = """<?xml version="1.0" encoding="UTF-8"?>
    <kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">
    <Document>
    	<name>KmlFile</name>
    	<Style id="sh_heliport">
    		<IconStyle>
    			<scale>3.19091</scale>
    			<Icon>
    				<href>http://maps.google.com/mapfiles/kml/shapes/heliport.png</href>
    			</Icon>
    			<hotSpot x="0.5" y="0" xunits="fraction" yunits="fraction"/>
    		</IconStyle>
    		<LabelStyle>
    			<color>00ffffff</color>
    			<scale>0.8</scale>
    		</LabelStyle>
    		<ListStyle>
    		</ListStyle>
    	</Style>
    	<Style id="sn_heliport">
    		<IconStyle>
    			<scale>2.7</scale>
    			<Icon>
    				<href>http://maps.google.com/mapfiles/kml/shapes/heliport.png</href>
    			</Icon>
    			<hotSpot x="0.5" y="0" xunits="fraction" yunits="fraction"/>
    		</IconStyle>
    		<LabelStyle>
    			<color>00ffffff</color>
    			<scale>0.8</scale>
    		</LabelStyle>
    		<ListStyle>
    		</ListStyle>
    	</Style>
    	<StyleMap id="msn_heliport">
    		<Pair>
    			<key>normal</key>
    			<styleUrl>#sn_heliport</styleUrl>
    		</Pair>
    		<Pair>
    			<key>highlight</key>
    			<styleUrl>#sh_heliport</styleUrl>
    		</Pair>
    	</StyleMap>
    	<Placemark>
    		<name>Test Placemark</name>
    		<LookAt>
    			<longitude>-120.0876437263338</longitude>
    			<latitude>33.91092166213198</latitude>
    			<altitude>0</altitude>
    			<range>270552.9282262918</range>
    			<tilt>0</tilt>
    			<heading>-17.23039679415411</heading>
    			<altitudeMode>relativeToGround</altitudeMode>
    			<gx:altitudeMode>relativeToSeaFloor</gx:altitudeMode>
    		</LookAt>
    		<styleUrl>#msn_heliport</styleUrl>
    		<Point>
    			<coordinates>-120.0876437263338,33.91092166213198,0</coordinates>
    		</Point>
    	</Placemark>
    	<NetworkLink>
        	<name>another link</name>
        	<Link>
        		<href>../media/layers/uploaded-kml/publicDataLayers.kmz</href>
        	</Link>
        </NetworkLink>
    </Document>
    </kml>
    """
    response = HttpResponse(content)
    return response