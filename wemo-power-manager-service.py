#!/usr/bin/python3

import re
import urllib3
import psutil
import sys, time
import socket


# Configuration:
# Enter the local IP address of your WeMo in the parentheses of the ip variable below. 
# You may have to check your router to see what local IP is assigned to the WeMo.
# It is recommended that you assign a static local IP to the WeMo to ensure the WeMo is always at that address.
# Uncomment one of the triggers at the end of this script.

min_battery_percentage = 30
max_battery_percentage = 80

ip = '192.168.1.148' # DEFAULT IP
hostname = "wemo"
try:
    ip = socket.gethostbyname(hostname)
except socket.error as err:
    print ("%s: %s"  %(hostname, err))
print ("Final WeMo IP Address: %s" %ip)


class wemo:
    OFF_STATE = '0'
    ON_STATES = ['1', '8']
    ip = None
    ports = [49153, 49152, 49154, 49151, 49155]
    http = None

    def __init__(self, switch_ip):
        self.ip = switch_ip
        self.http = urllib3.PoolManager()

    def toggle(self):
        status = self.status()
        if status in self.ON_STATES:
            result = self.off()
            result = 'WeMo is now off.'
        elif status == self.OFF_STATE:
            result = self.on()
            result = 'WeMo is now on.'
        else:
            raise Exception("UnexpectedStatusResponse")
        return result    

    def on(self):
        return self._send('Set', 'BinaryState', 1)

    def off(self):
        return self._send('Set', 'BinaryState', 0)

    def status(self):
        return self._send('Get', 'BinaryState')

    def name(self):
        return self._send('Get', 'FriendlyName')

    def signal(self):
        return self._send('Get', 'SignalStrength')

    def _get_header_xml(self, method, obj):
        method = method + obj
        return '"urn:Belkin:service:basicevent:1#%s"' % method
   
    def _get_body_xml(self, method, obj, value=0):
        method = method + obj
        return '<u:%s xmlns:u="urn:Belkin:service:basicevent:1"><%s>%s</%s></u:%s>' % (method, obj, value, obj, method)
	
    def _send(self, method, obj, value=None):
        body_xml = self._get_body_xml(method, obj, value)
        header_xml = self._get_header_xml(method, obj)
        for port in self.ports:
            result = self._try_send(self.ip, port, body_xml, header_xml, obj) 
            if result is not None:
                self.ports = [port]
            return result
        raise Exception("TimeoutOnAllPorts")

    def _try_send(self, ip, port, body, header, data):
        try:
            print (body)
            print (header)
            #request.add_header('Content-type', 'text/xml; charset="utf-8"')
            #request.add_header('SOAPACTION', header)
            request_body = '<?xml version="1.0" encoding="utf-8"?>\n\
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">\n\
   <s:Body>\n\
      %s\n\
   </s:Body>\n\
</s:Envelope>' % body
			
			
            request = self.http.request('POST', 'http://%s:%s/upnp/control/basicevent1' % (ip, port),
				headers={'Content-type': 'text/xml; charset="utf-8"', 'SOAPACTION': header},
				body=request_body)
            status_code = request.status
            print ("RESPONSE:", status_code)
            if status_code >= 400:
                quit()
            print(request.data)
            return self._extract(request.data.decode('utf-8'), data)
        except Exception as e:
            print (str(e))
            return quit()

    def _extract(self, response, name):
        exp = '<%s>(.*?)<\/%s>' % (name, name)
        g = re.search(exp, response)
        if g:
            return g.group(1)
        return response

def output(message):
    print (message)

switch = wemo(ip)

# Debug: Uncomment only one of the lines below to make the script work.

#output(switch.on())
output(switch.off())
#output(switch.toggle())
#output(switch.status())

print ("STARTING")
while True:
    battery = psutil.sensors_battery()
    plugged = battery.power_plugged
    percent = battery.percent
    if percent < min_battery_percentage:
        output(switch.on())
    if percent >= 80:
        output(switch.off())
    print("Battery: ", percent)
    print("-------------------------------------------------")
    sys.stdout.flush()
    time.sleep(60)
