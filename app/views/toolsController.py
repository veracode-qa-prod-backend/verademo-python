# toolsController.py deals with the 'Tools' page and calls the tool functions used in the page
import logging
import subprocess
import os
import shlex
import re


from django.shortcuts import render
from app.fortune.fortuneData import FortuneData, RiddleData



logger = logging.getLogger("VeraDemo:toolsController")

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
    request.file = fortune(fortunefile) if fortunefile else ""
    request.host = host
    request.ping = ping(host) if host else ""
    
    

    return render(request, 'app/tools.html', {"host" : host})

# pings selected host and outputs the result
def ping(host):
    output = ""
    logger.info("Pinging " + host)

    # Validate host input - allow only alphanumeric, dots, hyphens, and colons (for IPv6)
    if not re.match(r'^[a-zA-Z0-9.:-]+$', host):
        logger.error("Invalid host format")
        return "ping: invalid host format"

    try:
        # Use subprocess.run with list arguments and shell=False for safety
        result = subprocess.run(['ping', '-c', '1', host],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              timeout=5,
                              check=False,
                              shell=False)
        
        output = result.stdout.decode() if result.stdout else ""
        logger.info(output)
        logger.info("Exit Code:", result.returncode)
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
    # Fixed: Use subprocess.run with list arguments instead of os.system
    else:
        # Validate file input - allow only alphanumeric, dots, hyphens, and underscores
        if not re.match(r'^[a-zA-Z0-9._-]+$', file):
            logger.error("Invalid file format")
            return "Error: invalid file format"

        try:
            # Use subprocess.run with list arguments and shell=False for safety
            result = subprocess.run(['cat', file],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  check=False,
                                  shell=False)

            output = result.stdout.decode() if result.stdout else ""
            if result.returncode != 0:
                logger.error(f"Error reading file: {result.stderr.decode()}")
                return "Error reading file"
            return output
        except Exception as e:
            logger.error(f"Error executing cat command: {e}")
            return "Error reading file"
   
        




   