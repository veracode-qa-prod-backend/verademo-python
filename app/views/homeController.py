# homeController.py deals with the default website redirection.

from django.shortcuts import redirect
from .userController import login
import urllib

# redirects user to feed if they are already logged in, otherwise sends to login
def home(request):
    # Equivalent of HomeController.java
    if request.session.get('username'):
        # CWE-73 Fix: Use allow-list to prevent path traversal
        try:
            # TODO: Configure these allowed URLs for your application's valid redirect targets
            ALLOWED_URLS = [
                'http://localhost:8000/feed',
                'http://127.0.0.1:8000/feed',
                # Add other valid URLs here
            ]

            # Construct the tainted URL from user input
            host_ip = request.META['HTTP_HOST'].split(':')[0]
            print("da")
            tainted_url = 'http://' + host_ip + ':' + request.META['SERVER_PORT'] + '/feed'

            # Validate against allow-list and retrieve untainted URL
            if tainted_url not in ALLOWED_URLS:
                raise ValueError(f'Invalid redirect URL: {tainted_url}')

            url_index = ALLOWED_URLS.index(tainted_url)
            safe_url = ALLOWED_URLS[url_index]  # Use untainted URL from allow-list

            redir = urllib.request.Request(safe_url)
            urllib.request.urlopen(redir, timeout=5)
        except: 
            # GOOD CODE:
            print("redir")
            return redirect('feed')
    
    return login(request)