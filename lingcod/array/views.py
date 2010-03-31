from django.http import HttpResponse
from django.shortcuts import render_to_response
from lingcod.common import utils 
from django.conf import settings

Mpa = utils.get_mpa_class()
MpaArray = utils.get_array_class()

def add_mpa(request, pk):
    '''
        Add and MPA to a given array
    '''
    if request.method == 'POST':
        try:
            mpa_id = request.REQUEST['mpa_id']
        except:
            return HttpResponse( "Must supply an 'mpa_id' parameter.", status=500 )

        # Make sure user owns both the array and MPA
        user = request.user
        if user.is_anonymous() or not user.is_authenticated():
            return HttpResponse('You must be logged in', status=401)

        # Get MPA object 
        # print Mpa.objects.all()
        try:
            the_mpa = Mpa.objects.get(user=user,id=mpa_id)
        except:
            return HttpResponse( user.username + " does not own an MPA with ID " + mpa_id, status=404 )

        # If MPA already has an array, remove it then proceed
        if the_mpa.array:
            the_mpa.remove_from_array()

        # Get array object
        try:
            the_array = MpaArray.objects.get(user=user,id=pk)
        except:
            return HttpResponse( user.username + " does not own an Array with ID " + pk, status=404 )

        # Add the MPA to the array
        the_mpa.add_to_array(the_array)
        return HttpResponse("Added mpa %s to array %s" % (mpa_id, pk))
    else:
        return HttpResponse( "Array-MPA service received unexpected " + request.method + " request.", status=400 )

def remove_mpa(request, pk):
    '''
        Remove an MPA from its array
    '''
    if request.method == 'POST':
        try:
            mpa_id = request.REQUEST['mpa_id']
        except:
            return HttpResponse( "Must supply an 'mpa_id' parameter.", status=500 )

        # Make sure user owns MPA
        user = request.user
        if user.is_anonymous() or not user.is_authenticated():
            return HttpResponse('You must be logged in', status=401)

        # Get MPA object 
        try:
            the_mpa = Mpa.objects.get(user=user,id=mpa_id)
        except:
            return HttpResponse( user.username + " does not own an MPA with ID " + mpa_id, status=404 )

        # If MPA is not in any array, return an error since there is nothing to remove
        if not the_mpa.array:
            return HttpResponse( "MPA " + mpa_id + " is not associated with another array (nothing to remove).", status=500 )

        # Get array object and make sure it is owned by user 
        try:
            the_array = MpaArray.objects.get(user=user,id=pk)
        except:
            return HttpResponse( user.username + " does not own an Array with ID " + pk, status=404 )
        # and make sure we're trying to remove it from the right array
        if the_mpa.array != the_array:
            return HttpResponse( "Trying to remove mpa %s from array %s but it currently belongs to another array " % 
                                  (mpa_id, pk), status=500 )

        # Remove the MPA from the array
        the_mpa.remove_from_array()
        return HttpResponse("Removed MPA %s from array %s" % (mpa_id, pk))
    else:
        return HttpResponse( "Array-MPA service received unexpected " + request.method + " request.", status=400 )


def copy(request, pk):
    """
    Creates a copy of the given array 
    On success, Return status 201 with Location set to new MPA
    Permissions: Need to either own or have shared with you to make copy
    """
    if request.method == 'POST':
        # Authenticate
        user = request.user
        if user.is_anonymous() or not user.is_authenticated():
            return HttpResponse(txt + 'You must be logged in', status=401)

        from lingcod.sharing.utils import can_user_view
        viewable, response = can_user_view(MpaArray, pk, user) 
        if not viewable:
            return response
        else:
            the_array = MpaArray.objects.get(pk=pk)
        
        # Go ahead and make a copy
        new_array = the_array.copy(user)

        Location = new_array.get_absolute_url()
        res = HttpResponse("A copy of Array %s was made; see %s" % (pk, Location), status=201)
        res['Location'] = Location
        return res
    else:
        return HttpResponse( "Array copy service received unexpected " + request.method + " request.", status=400 )


def download_supportfile(request, pk, filenum):
    if request.method == 'GET':
        # Authenticate
        user = request.user
        from lingcod.sharing.utils import can_user_view
        viewable, response = can_user_view(MpaArray, pk, user) 
        if not viewable:
            return response
        else:
            the_array = MpaArray.objects.get(pk=pk)

        import os
        filenum = int(filenum)
        if filenum == 1:
            fpath = os.path.realpath(os.path.join(settings.MEDIA_ROOT, the_array.supportfile1.name))
            filename = the_array.supportfile1_shortname
        elif filenum == 2:
            fpath = os.path.realpath(os.path.join(settings.MEDIA_ROOT, the_array.supportfile2.name))
            filename = the_array.supportfile2_shortname
        else:
            return HttpResponse('File number does not exist', status=404)

        if os.path.exists(fpath):
            import mimetypes
            mimetype = mimetypes.guess_type(fpath)[0] or 'application/octet-stream'

            f = file(fpath)
            try:
                content = f.read(os.path.getsize(fpath))
            finally:
                f.close()

            response = HttpResponse(content, mimetype=mimetype)
            response['Content-Disposition']='attachment; filename="%s"'%filename
            response["Content-Length"] = len(content)
            return response
        else:
            return HttpResponse('File does not exist', status=404)

