from django.contrib.auth import logout as log_them_out
from lingcod.digest.models import DigestSession
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

def logout(request):
    if request.user.is_authenticated():
        print "authenticated"
        DigestSession.objects.expire_sessions(request.user)
    print "about to logout"
    log_them_out(request)
    print "logged out"
    return HttpResponseRedirect(reverse('map'))
    
    