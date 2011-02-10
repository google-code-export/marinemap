
# Designed for OSX / Firefox

import time
time.sleep(5)

from windmill.authoring import WindmillTestClient

def test_recordingSuite0():
    client = WindmillTestClient(__name__)

    client.click(link=u'sign in')
    client.waits.sleep(milliseconds=u'5000')
    client.waits.forPageLoad(timeout=u'20000')
    client.waits.sleep(milliseconds=u'5000')
    client.type(text=u'windmill', id=u'id_username')
    client.waits.sleep(milliseconds=u'5000')
    client.type(text=u'@mmap!', id=u'id_password')
    client.waits.sleep(milliseconds=u'5000')
    client.click(name=u'blogin')
    client.waits.sleep(milliseconds=u'5000')
    client.waits.forPageLoad(timeout=u'20000')
    client.waits.sleep(milliseconds=u'5000')


