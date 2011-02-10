
# designed for OSX \ Firefox

import time
time.sleep(5)

from windmill.authoring import WindmillTestClient

def test_recordingSuite0():
    client = WindmillTestClient(__name__)

    client.click(xpath=u"//li[@id='kml-kml-f404174b8294872d436dac74c591043e-windmill-shared_mpa_links-kmzMarine-Protected-Areas-and-ArraysPublic-Proposals']/div[1]")
    client.waits.sleep(milliseconds=u'5000')
    client.click(xpath=u"//li[@id='kmlhttp---northcoast-marinemap-org-kml-f404174b8294872d436dac74c591043e-public-kmzMarine-Protected-Areas-and-ArraysExternal-MPA-Array-A']/div[1]")
    client.waits.sleep(milliseconds=u'5000')
    client.click(xpath=u"//li[@id='kmlhttp---northcoast-marinemap-org-kml-f404174b8294872d436dac74c591043e-public-kmzMarine-Protected-Areas-and-ArraysExternal-MPA-Array-A']/div[2]")
    client.waits.sleep(milliseconds=u'5000')
    client.click(xpath=u"//li[@id='kmlhttp---northcoast-marinemap-org-kml-f404174b8294872d436dac74c591043e-960-array-kmzMarine-Protected-Areas-and-ArraysPyramid-Point--FS--SMCA']/span")
    client.waits.sleep(milliseconds=u'5000')
    client.click(xpath=u"//div[@id=':b']/div/div")
    client.waits.sleep(milliseconds=u'5000')
    client.click(xpath=u"//div[@id='panel-holder']/div[3]/a/img")
    client.waits.sleep(milliseconds=u'5000')
    client.click(xpath=u"//li[@id='kmlhttp---northcoast-marinemap-org-kml-f404174b8294872d436dac74c591043e-public-kmzMarine-Protected-Areas-and-ArraysExternal-MPA-Array-A']/div[2]")
    client.waits.sleep(milliseconds=u'5000')
    client.click(xpath=u"//li[@id='kmlhttp---northcoast-marinemap-org-kml-f404174b8294872d436dac74c591043e-public-kmzMarine-Protected-Areas-and-ArraysExternal-MPA-Array-A']/div[1]")
    client.waits.sleep(milliseconds=u'5000')
    client.click(xpath=u"//li[@id='kml-kml-f404174b8294872d436dac74c591043e-windmill-shared_mpa_links-kmzMarine-Protected-Areas-and-ArraysPublic-Proposals']/div[1]")
    client.waits.sleep(milliseconds=u'5000')


