# encoding: UTF-8
# cachetoi.py
# 
# Cache-toi !
# French for “Hide!”

import sha
from datetime import datetime
import re

class CacheToi:
  def get(self, *args, **kwargs):
    answerer, do_once = None, False
    try:
      answerer  = self.get_once
      do_once   = True
    except AttributeError:
      try:
        answerer  = self.cached_get
      except AttributeError:
        self.response.set_status(500)
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Implement cache-aware methods: get_once/cached_get, latest. Cache me if you can.')
        return
    self.response.headers['Cache-Control'] = 'public'
    if do_once:
      if self.request.headers.get('If-None-Match') or self.request.headers.get('If-Modified-Since'):
        self.response.set_status(304)
        return
    latest  = datetime.now() if do_once else self.latest(*args, **kwargs)
    etag    = sha.new(str(latest)).hexdigest()
    self.response.headers['ETag'] = etag
    if etag == self.request.headers.get('If-None-Match'):
      self.response.set_status(304)
      return
    if self.request.headers.get('If-Modified-Since'):
      temps = self.request.headers.get('If-Modified-Since')
      got = re.match(r'[^ ]+ (\d+) (\w+) (\d+) (\d+):(\d+):(\d+)', temps)
      if got:
        previously  = datetime(day = int(got.group(1)), month = 'Months: Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split(' ').index(got.group(2)), year = int(got.group(3)), hour = int(got.group(4)), minute = int(got.group(5)), second = int(got.group(6)), microsecond = latest.microsecond)
        if previously >= latest:
          self.response.set_status(304)
          return
    answerer(*args, **kwargs)
