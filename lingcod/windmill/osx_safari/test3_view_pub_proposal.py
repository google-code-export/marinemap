
#   designed for OSX / Safari

import time
time.sleep(5)

from windmill.authoring import WindmillTestClient

def test_recordingSuite0():
    client = WindmillTestClient(__name__)

    client.click(xpath=u"//li[@id='kml-kml-8122ae67e7cc28288bac1e8d48233ef5-windmill-shared_mpa_links-kmzMarine-Protected-Areas-and-ArraysPublic-Proposals']/div[1]")
    client.waits.sleep(milliseconds=u'5000')
    client.click(xpath=u"//li[@id='kmlhttp---northcoast-marinemap-org-kml-8122ae67e7cc28288bac1e8d48233ef5-public-kmzMarine-Protected-Areas-and-ArraysExternal-MPA-Array-A']/div[1]")
    client.waits.sleep(milliseconds=u'5000')
    client.click(xpath=u"//li[@id='kmlhttp---northcoast-marinemap-org-kml-8122ae67e7cc28288bac1e8d48233ef5-public-kmzMarine-Protected-Areas-and-ArraysExternal-MPA-Array-A']/div[2]")
    client.waits.sleep(milliseconds=u'5000')
    client.click(xpath=u"//li[@id='kmlhttp---northcoast-marinemap-org-kml-8122ae67e7cc28288bac1e8d48233ef5-960-array-kmzMarine-Protected-Areas-and-ArraysPyramid-Point--FS--SMCA']/span")
    client.waits.sleep(milliseconds=u'5000')
    client.click(xpath=u"//div[@id=':b']/div/div")
    client.waits.sleep(milliseconds=u'5000')
    client.click(xpath=u"//div[@id='panel-holder']/div[3]/a/img")
    client.waits.sleep(milliseconds=u'5000')
    client.click(xpath=u"//li[@id='kmlhttp---northcoast-marinemap-org-kml-8122ae67e7cc28288bac1e8d48233ef5-public-kmzMarine-Protected-Areas-and-ArraysExternal-MPA-Array-A']/div[2]")
    client.waits.sleep(milliseconds=u'5000')
    client.click(xpath=u"//li[@id='kmlhttp---northcoast-marinemap-org-kml-8122ae67e7cc28288bac1e8d48233ef5-public-kmzMarine-Protected-Areas-and-ArraysExternal-MPA-Array-A']/div[1]")
    client.waits.sleep(milliseconds=u'5000')
    client.click(xpath=u"//li[@id='kml-kml-8122ae67e7cc28288bac1e8d48233ef5-windmill-shared_mpa_links-kmzMarine-Protected-Areas-and-ArraysPublic-Proposals']/div[1]")


