
#  designed for OSX / Firefox

import time
time.sleep(5)

from windmill.authoring import WindmillTestClient

def test_recordingSuite3():
    client = WindmillTestClient(__name__)

    client.click(link=u'sign out')
    client.waits.sleep(milliseconds=u'5000')


