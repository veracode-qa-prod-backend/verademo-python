# toolsController.py deals with the 'Tools' page and calls the tool functions used in the page
import logging
import subprocess
import os
import shlex
import re
from html import escape

from django.shortcuts import render
from app.fortune.fortuneData import FortuneData, RiddleData



logger = logging.getLogger("VeraDemo:toolsController")

# Allow-list for safe file paths in fortune command
SAFE_FORTUNE_FILES = {'fortunes', 'riddles', 'fortunes.txt', 'riddles.txt'}

def validate_host(host):
    """Validate that host is a safe hostname or IP address."""
    if not host:
        raise ValueError("Host cannot be empty")
    # Allow only alphanumeric, dots, hyphens, and colons (for IPv6)
    if not re.match(r'^[a-zA-Z0-9.:-]+$', host):
        raise ValueError("Invalid host format")
    # Prevent command injection attempts
    if any(char in host for char in [';', '&', '|', '$', '`', '\n', '\r']):
        raise ValueError("Invalid characters in host")
    return True

def validate_fortune_file(file):
    """Validate that the fortune file is in the allow-list."""
    if file in SAFE_FORTUNE_FILES:
        return True
    # Also allow files in the fortunes directory with safe names
    if file.startswith('fortunes/') or file.startswith('./fortunes/'):
        basename = os.path.basename(file)
        if re.match(r'^[a-zA-Z0-9_-]+\.txt$', basename):
            return True
    raise ValueError(f"Fortune file not allowed: {file}")

# Redirects request based on type
def tools(request):
    if(request.method == "GET"):
        return showTools(request)
    elif(request.method == "POST"):
        return processTools(request)

# Loads the tool webpage    
def showTools(request):
    request.host = ""
    return render(request, 'app/tools.html', {})

# Performs the actions on the tool page, updating output accordingly
def processTools(request):
    host = request.POST.get('host')
    fortunefile = request.POST.get('fortunefile')

    # Process fortune file and escape output
    fortune_output = fortune(fortunefile) if fortunefile else ""
    request.file = escape(fortune_output) if fortune_output else ""

    # Process ping and escape all outputs
    ping_output = ping(host) if host else ""
    request.ping = escape(ping_output) if ping_output else ""
    request.host = escape(host) if host else ""
    
    # Escape user input to prevent XSS
    safe_host = escape(host) if host else ""

    return render(request, 'app/tools.html', {"host" : safe_host})

# pings selected host and outputs the result
def ping(host):
    output = ""
    logger.info("Pinging " + host)
    try:
        # Validate host before executing command
        validate_host(host)

        # Use subprocess.run with shell=False for security
        result = subprocess.run(['ping', '-c', '1', host],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              timeout=5,
                              shell=False)
        
        output = result.stdout.decode() if result.stdout else ""
        logger.info(output)
        logger.info("Exit Code:", result.returncode)
    except ValueError as ve:
        logger.error("Invalid host: %s", ve)
        output = "ping: invalid host " + host
    except subprocess.TimeoutExpired:
        logger.error("Ping timed out")
        output = "ping: unknown host " + host
    except Exception as e:  
        logger.error("Error", e)
        output = "ping: unknown host " + host

    return output


# Produces a fortune based on the submitted selection
def fortune(file):
    if file=='fortunes':
        return FortuneData()
    elif file == 'riddles':
        return RiddleData()
    # Use subprocess.run with list arguments and shell=False for security
    else:
        try:
            # Validate file path before executing command
            validate_fortune_file(file)

            result = subprocess.run(['cat', file],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  shell=False,
                                  timeout=5)
            return result.stdout.decode() if result.stdout else ""
        except ValueError as ve:
            logger.error("Invalid fortune file: %s", ve)
            return ""
        except Exception as e:
            logger.error("Error reading file", e)
            return ""
   
        




   