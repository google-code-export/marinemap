#!/usr/bin/python

#import windmill
#import functest
#from windmill.authoring import WindmillTestClient

# Designed for OSX / Safari

def test_recordingSuite0():
    client = WindmillTestClient(__name__)

    client.click(xpath=u"//div[@id='panel-holder']/div[3]/a/img")
    client.waits.sleep(milliseconds=u'5000')
    client.click(id=u'news')
    client.waits.sleep(milliseconds=u'5000')
    client.click(xpath=u"//div[@id='panel-holder']/div[3]/a/img")
    client.waits.sleep(milliseconds=u'5000')
    client.click(id=u'about')
    client.waits.sleep(milliseconds=u'5000')
    client.click(xpath=u"//li[@id='layers_menu']/span/a/img")
    client.waits.sleep(milliseconds=u'5000')
    client.click(xpath=u"//li[@id='layers_menu']/a/img")
    client.waits.sleep(milliseconds=u'5000')
    client.click(xpath=u"//li[@id='tools_menu']/span/a/img")
    client.waits.sleep(milliseconds=u'5000')
    client.click(xpath=u"//li[@id='tools_menu']/a/img")
    client.waits.sleep(milliseconds=u'5000')
    client.click(id=u'sidebar-toggler')
    client.waits.sleep(milliseconds=u'5000')
    client.click(id=u'show-sidebar')
