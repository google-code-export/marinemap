from lingcod.digest.models import DigestSession, get_random
from datetime import datetime

def digest_or_cookie_authentication(hours=24, domain='/'):
    def inner_function(f):
        
        def inner_view(request, *args, **kwargs):
            
            # if request.user.is_authenticated() and not request.user.is_anonymous():
            #     # If already logged in with a cookie, do nothing
            #     return f(request, *args, **kwargs)
                
            params = DigestSession.objects.parse(request)
            session = DigestSession.objects.find_or_create(params)
            if session.authenticates(params, request):
                if session.is_stale(hours):
                    session.nonce = get_random()
                    session.created = datetime.now()
                    session.save()
                    response = session.generate_challenge(domain=domain, stale=True)
                    print "authorization header"
                    print response['WWW-Authenticate']
                    return response                    
                else:
                    print "found session"
                    request.user = session.user
                    return f(request, *args, **kwargs)
            else:
                response = session.generate_challenge(domain=domain)
                return response
            
        print "Exited", f.__name__
        
        return inner_view
    return inner_function