from windmill.authoring import WindmillTestClient

def test_recordingSuite0():
    client = WindmillTestClient(__name__)

    client.click(link=u'sign out')
    client.waits.forPageLoad(timeout=u'20000')
    client.waits.sleep(milliseconds=u'7000')
