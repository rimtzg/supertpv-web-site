try:
    from urllib.parse import urlparse, urlencode
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError
except ImportError:
    from urlparse import urlparse
    from urllib import urlencode
    from urllib2 import urlopen, Request, HTTPError

import logging
from bson.json_util import dumps, loads
import json

from translate import _

def MakeBson(json_raw):
    text = json.dumps(json_raw)
    json_data = json.loads(text)
    bson_data = loads(json_data)
    return bson_data

def MakeJson(cursor):
    text = dumps(cursor)
    bytes = text.encode()
    return bytes

class Connection:
    def __init__(self, server_url='localhost', server_port='5000', timeout=30):
        self.server_url = server_url
        self.server_port = server_port
        self.timeout = timeout

    def send(self, get_url=None, data=None):
        response = None

        url = str(self.server_url)
        if(self.server_port):
            url = url + ':' + str(self.server_port)

        if(get_url):
            url = url+get_url

        logging.info(_('Url: ')+str(url))

        if(data):
            data = MakeJson(data)

        logging.info(_('Data sent: ')+str(data))
        try:
            req = Request(url)
            req.add_header('Content-Type', 'application/json')

            response = urlopen(req, data, self.timeout)

        except HTTPError as e:
            logging.warn( e.reason )
        except:
            logging.warn(_('Error in the connection with the server'))

        if(response):
            result = response.read()
            logging.info('Response: ' + str(result))
            try:
                return MakeBson(result)
            except TypeError as e:
                logging.exception(e)
                return None
        else:
            return None