
#  Designed for OSX / Safari

import time
time.sleep(5)

from windmill.authoring import WindmillTestClient

def test_recordingSuite1():
    client = WindmillTestClient(__name__)

    client.click(xpath=u"//div[@id='sidebar']/ul/li[1]/a/span")
    client.waits.sleep(milliseconds=u'5000')
    client.click(xpath=u"//li[@id='kml-kml-8122ae67e7cc28288bac1e8d48233ef5-windmill-user_mpa_links-kmzMarine-Protected-Areas-and-ArraysMarine-Protected-Areas']/div[1]")
    client.waits.sleep(milliseconds=u'5000')
    client.click(xpath=u"//li[@id='kml-kml-8122ae67e7cc28288bac1e8d48233ef5-windmill-user_mpa_links-kmzMarine-Protected-Areas-and-ArraysMarine-Protected-AreasTest-Shape']/div[2]")
    client.waits.sleep(milliseconds=u'5000')
    client.click(xpath=u"//li[@id='kml-kml-8122ae67e7cc28288bac1e8d48233ef5-windmill-user_mpa_links-kmzMarine-Protected-Areas-and-ArraysMarine-Protected-AreasTest-Shape']/span")
    client.waits.sleep(milliseconds=u'5000')
    client.click(xpath=u"//div[@id=':3']/div/div")
    client.waits.sleep(milliseconds=u'5000')
    client.click(xpath=u"//div[@id='panel-holder']/div[3]/a/img")
    client.waits.sleep(milliseconds=u'5000')
    client.click(xpath=u"//li[@id='kml-kml-8122ae67e7cc28288bac1e8d48233ef5-windmill-user_mpa_links-kmzMarine-Protected-Areas-and-ArraysMarine-Protected-Areas']/div[2]")
    client.waits.sleep(milliseconds=u'5000')
    client.click(xpath=u"//li[@id='kml-kml-8122ae67e7cc28288bac1e8d48233ef5-windmill-user_mpa_links-kmzMarine-Protected-Areas-and-ArraysMarine-Protected-Areas']/div[1]")
    client.waits.sleep(milliseconds=u'5000')
    client.click(xpath=u"//div[@id='sidebar']/ul/li[2]/a/span")
    client.waits.sleep(milliseconds=u'5000')
