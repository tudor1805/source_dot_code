# Django imports
from django.shortcuts import render
from django.template  import RequestContext, loader

from django.core.files.base    import ContentFile
from django.core.files.storage import default_storage

from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.http         import Http404, HttpResponse
from django.shortcuts    import redirect

from rest_framework.compat import BytesIO
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

# Models
from uploads.models import User, Paste

# Misc
import random
import string

# Debug
from pprint import pprint

# Use Client
import sys
sys.path.insert(0, '/home/wizard/CAAS/source_dot_code/build_agent/')
from build_agent.submit_client import SubmitClient
import common


import json

def get_server_ip_port(request):
     import socket
     return request.META['HTTP_HOST']
     #return request.META['HTTP_HOST'] + ":" + request.META['SERVER_PORT']
#     pprint(request.META)
#     return socket.gethostbyname(request.META['HTTP_HOST']) + ":" + request.META['SERVER_PORT']
#     retrn 

############################

class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

@csrf_exempt
def compile_code(request):
    if request.method == 'GET':
        raise Http404
    elif request.method == 'POST':
        # Parse the request, extract the fields ...
        try:
            data = json.loads(request.body)
        except:
            return JSONResponse('{ "error": "Cannot parse JSON" }')

        language   = data.get('lang', '')
        code       = data.get('code', '')
        hash_id = generate_id(5)

        try:
           paste = Paste.create(hash_id, language, True, code, "")
        except:
           raise Http404

        file_name='test.c'
        codeSubmit = common.CodeSubmit(file_name, paste.code, paste.language)
        client = SubmitClient('127.0.0.1', 54321, codeSubmit)
        paste.output = client.result.warnings + client.result.output
        paste.save()

        print paste.output

        # Construct response based on output
        response = {}
        response['output']     = paste.output
        response['paste_link'] = "http://" + get_server_ip_port(request) + "/uploads/paste/" + paste.hash_id 
        return JSONResponse(json.dumps(response))
    else:
        raise Http404
############################

def generate_id(size=6, chars=string.ascii_uppercase + string.digits):
    while True:
        new_id = ''.join(random.choice(chars) for x in range(size))
        # The generated id must be unique
        try:
            existing_paste = Paste.objects.get(hash_id=new_id)
        except Paste.DoesNotExist:
            break
    return new_id

def edituser(request, username):
    # Get user object
    if request.user.is_authenticated():
        user = User.objects.get(id=request.user.id)
    else:
        return HttpResponse('Unauthorized', status=401)

    if request.method == 'GET':
        return render(request, 'uploads/user_edit.html', {'user' : user})
    elif request.method == 'POST':
        firstname = request.POST.get('firstname', '')
        lastname  = request.POST.get('lastname', '')
        email     = request.POST.get('email', '')
        print "==="
        pprint(request.POST)
        user.first_name = firstname 
        user.last_name  = lastname 
        user.email      = email
        user.save()
        return redirect('/uploads/users/' + username)
    else:
        raise Http404

def pastecode(request):
   # Extract user for the request
   if request.user.is_authenticated():
       user = User.objects.get(id=request.user.id)
   else:
       user = None

   language   = request.POST.get('lang', '')
   code       = request.POST.get('code', '')
   is_private = request.POST.get('private', '')
   run        = request.POST.get('run', '')

   hash_id = generate_id(5)
   try:
       paste = Paste.create(hash_id, language, is_private, code, "")
       paste.user   = user
   except:
       raise Http404

   # Run code, if requested
   if run:
       file_name='test.c'
       codeSubmit = common.CodeSubmit(file_name, paste.code, paste.language)
       client = SubmitClient('127.0.0.1', 54321, codeSubmit)
       paste.output = client.result.warnings + client.result.output
   paste.save()
   return redirect('uploads.views.viewpaste', hash_id=hash_id)

   
def forkpaste(request, hash_id):
    if request.method == 'GET':
        # Get paste object based on the hash id
        try:
            paste = Paste.objects.get(hash_id=hash_id)
        except Paste.DoesNotExist:
            raise Http404
        return render(request, 'uploads/fork.html',
                      {'paste':paste})
    elif request.method == 'POST':
        return pastecode(request)
    else:
        raise Http404
       

def showuser(request, username):
    # Retrieve user
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404

    # Retrieve user pastes
    userPastes = Paste.objects.filter(user=user)
    return render(request, 'uploads/user.html',
                  {'user' : user,
                   'userPastes' : userPastes})

def rawpaste(request, hash_id):
    if request.method == 'GET':
        # Get paste object based on the hash id
        try:
            paste = Paste.objects.get(hash_id=hash_id)
        except Paste.DoesNotExist:
            raise Http404

        code_file = ContentFile(paste.code)

        # Create a response object containing the file
        response = HttpResponse(code_file, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="raw.c"'
        return response
    else:
        raise Http404

def viewpaste(request, hash_id):
    if request.method == 'GET':
        # Get paste object based on the hash id
        try:
            paste = Paste.objects.get(hash_id=hash_id)
        except Paste.DoesNotExist:
            raise Http404

        # Prepare response
        return render(request, 'uploads/show_paste.html',
                     {'paste' : paste})
    else:
        raise Http404

def logout(request):
    # It's safer to handle logout requests as POST
    if request.method == 'POST':
        auth_logout(request)
        return redirect('uploads.views.index')
    else:
        raise Http404

def login(request):
    if request.method == 'GET':
        # We want the login form
        return render(request, 'uploads/login.html')
    elif request.method == 'POST':
        # We want to log in
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        user = authenticate(username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('uploads.views.index')
        else:
            error_message = "No such User"
            return render(request, 'uploads/login.html',
                          {'error_message' : error_message})
    else:
        raise Http404

def mkacct(request):
    if request.method == 'POST':
        # Get parameters
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        if not username or not password:
            # TODO remove from here
            print "Error. empty fields"
            raise Http404

        # Create user account
        try:
            user = User.objects.create_user(username, password)
            user.save()
        except:
            error_message = "Invalid username. Usernames must be between 3 and 40 characters, and cannot contain whitespace."
            return render(request, 'uploads/login.html',
                          {'error_message' : error_message})

        return redirect('uploads.views.index')
    else:
        raise Http404

def submit(request):
    if request.method == 'POST':
        pprint(request.POST)
        return pastecode(request)
    else:
        raise Http404

def about(request):
    if request.method == 'GET':
        return render(request, 'uploads/about.html')
    else:
        raise Http404

def index(request):
    if request.method == 'GET':
        return render(request, 'uploads/index.html',
                      {'is_index_page' : 1})
    else:
        raise Http404
