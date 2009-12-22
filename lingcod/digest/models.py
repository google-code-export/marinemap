from django.contrib.gis.db import models
from django.contrib.auth.models import User, Group
from django.http import HttpResponse
from datetime import datetime, timedelta
import urllib2
import random
from hashlib import md5
from django.conf import settings

def get_random():
    return hex(random.getrandbits(128))[2:-1]

class DigestManager(models.GeoManager):

    def parse(self, request):
        print "request HTTP_AUTHORIZATION header"
        if request.META.has_key('HTTP_AUTHORIZATION'):
            print request.META['HTTP_AUTHORIZATION']
            items = urllib2.parse_http_list(
                request.META['HTTP_AUTHORIZATION'])
            return urllib2.parse_keqv_list(items)
        else:
            print 'request doesnt have http_authorization'
            return False

    def find_or_create(self, params):
        if params and params['opaque']:
            result = self.filter(opaque=params['opaque'])
            if len(result) == 1:
                print "found"
                return result[0]
        print "didnt find, creating"
        return self.create(created=datetime.now())

    def expire_sessions(self, user):
        self.filter(user=user).delete()
            

class DigestSession(models.Model):
    user = models.ForeignKey(User, blank=True, null=True)
    opaque = models.CharField(max_length=32, default=get_random, db_index=True, unique=True)
    nonce = models.CharField(max_length=32, default=get_random)
    created = models.DateTimeField()
    nc = models.IntegerField(default=0)
    ha1 = models.CharField(max_length=32, blank=True)
    
    objects = DigestManager()
    
    def authenticates(self, params, request):
        if params and params['opaque']:
            if params['opaque'] != self.opaque:
                print "opaque did not match"
                print params['opaque'], self.opaque
                return False
            if params['nonce'] != self.nonce:
                print "nonce did not match"
                return False

            if self.user is None:                
                try:
                    print params['Digest username']
                    user = User.objects.get(username=params['Digest username'])
                    self.user = user
                    self.save()
                except(e):
                    print e
                    print "could not find user"
                    return False
            
            if params['Digest username'] != self.user.username:
                print "username did not match"
                return False
            if params['realm'] != settings.REALM:
                print "realm did not match"
                return False
            # print "Okay, time for cryptography"
            # url = request.build_absolute_uri()
            url = request.get_full_path()
            # print url
            # print 'ha1 = %s' % (self.user.ha1, )
            ha2 = md5('%s:%s' % (request.method, url)).hexdigest()
            # print 'ha2 = %s:%s = %s' % (request.method, url, ha2)
            # print 'ha = %s:%s:%s' % (self.user.ha1, self.nonce ,ha2)
            ha = md5('%s:%s:%s' % (self.user.ha1,self.nonce,ha2)).hexdigest()
            # print ha, params['response']
            if ha == params['response']:
                return True
            else:
                print "did not match"
                return False
                

        print "fell through"
        print params
        return False
    
    def is_stale(self, hours):
        # print "now = %s" % (datetime.now(),) 
        # print "session time = %s" % (self.created, )
        return (datetime.now() - self.created) > timedelta (hours = hours)
        
    
    def generate_challenge(self, domain="/", stale=False):
        print "-- challenging"
        response = HttpResponse()
        response.status_code = 401
        if stale:
            response['WWW-Authenticate'] = 'Digest realm="%s",nonce="%s",opaque="%s",stale="TRUE",domain="/"' % (settings.REALM, self.nonce, self.opaque)
        else:
            response['WWW-Authenticate'] = 'Digest realm="%s",nonce="%s",opaque="%s",domain="/"' % (settings.REALM, self.nonce, self.opaque)

        print "authorization header"
        print response['WWW-Authenticate']        
        return response


# from django.db.models.signals import pre_save
# 
# def pre_save_user(sender, **kwargs):
#     print sender, kwargs['instance']
#     print kwargs
#     inst = kwargs['instance']
#     print inst.password
# 
# pre_save.connect(pre_save_user, sender=User)