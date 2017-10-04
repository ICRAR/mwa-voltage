#!/usr/bin/env python
#
#    ICRAR - International Centre for Radio Astronomy Research
#    (c) UWA - The University of Western Australia, 2014
#    Copyright by UWA (in the framework of the ICRAR)
#    All rights reserved
#
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 2.1 of the License, or (at your option) any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston,
#    MA 02111-1307  USA

import sys
import os
import time
import json
import threading
import urllib2
import urllib
import base64
import time
import datetime
import calendar
from optparse import OptionParser
from multiprocessing import Queue
from Queue import Empty

username = 'ngas'
password = 'ngas'

LOCK = threading.RLock()
ERRORS = []
COMPLETE = 0
TOTAL_FILES = 0

sec_const = 315964784

def GPSNow():
    return int(time.time()) - sec_const

def UTCToGPS(year, month, day, hour, minu, sec) :
    t = calendar.timegm((year, month, day, hour, minu, sec, -1, -1, 0))
    return t - sec_const

def file_error(err):
   global ERRORS
   with LOCK:
      ERRORS.append(err)
      print(err)

def file_starting(filename):
   with LOCK:
      print('%s [INFO] Downloading %s' % (time.strftime('%c'), filename))

def file_complete(filename):
   global COMPLETE
   global TOTAL_FILES
   with LOCK:
      COMPLETE = COMPLETE + 1
      print('%s [INFO] %s complete [%d of %d]' % (time.strftime('%c'), filename,
                                                  COMPLETE, TOTAL_FILES))

def split_raw_recombined(filename):

   try:
      file = os.path.basename(filename)
      if '.dat' not in file:
         raise Exception('dat extension not found')

      part = file.split('_')
      if 'ch' not in part[2]:
         raise Exception('ch not found in 3rd part')

      obsid = int(part[0])

      try:
         # 1070978272_1401856338_ch164.dat variant
         tm = int(part[1])
         chan = part[2].split('.')[0]

      except:
         #1070978272_c_ch05_1386943943.dat variant
         chan = part[2]
         tm = int(part[3].split('.')[0])

      dtm = datetime.datetime.utcfromtimestamp(int(tm))
      gps = UTCToGPS(dtm.year, dtm.month, dtm.day, dtm.hour, dtm.minute, dtm.second)
      return obsid, gps, chan

   except Exception as e:
      raise Exception('invalid voltage recombined product filename %s' % file)


def split_raw_voltage(filename):
   try:
      file = os.path.basename(filename)
      if '.dat' not in file:
         raise Exception('dat extension not found')

      part = file.split('_')
      if 'vcs' not in part[2]:
         raise Exception('vcs not found in 3rd part')

      return (int(part[0]), int(part[1]), part[2], int(part[3].split('.')[0]))

   except Exception as e:
      raise Exception('invalid voltage data filename %s' % file)


def split_ics(filename):
   try:
      file = os.path.basename(filename)
      if '.dat' not in file:
         raise Exception('dat extension not found')

      part = file.split('_')
      if 'ics' not in part[2]:
         raise Exception('ics not found in 3rd part')

      return int(part[0]), int(part[1])

   except Exception as e:
      raise Exception('invalid ics filename %s' % file)


def split_combined(filename):
   try:
      file = os.path.basename(filename)
      if '.tar' not in file:
         raise Exception('tar extension not found')

      part = file.split('_')
      if 'combined' not in part[2]:
         raise Exception('combined not found in 3rd part')

      return int(part[0]), int(part[1])

   except Exception as e:
      raise Exception('invalid combined filename %s' % file)


def query_observation(obs, host, filetype, timefrom, duration):

   processRange = False
   if timefrom != None and duration != None:
      processRange = True

   response = None
   try:
      url = 'http://%s/metadata/obs/?obs_id=%s' % (host, str(obs))
      request = urllib2.Request(url)
      response = urllib2.urlopen(request)

      resultbuffer = []
      while True:
        result = response.read(32768)
        if not result:
          break
        resultbuffer.append(result)

      keymap = {}
      files = json.loads(''.join(resultbuffer))['files']
      if processRange:
         second = None
         for f, v in files.iteritems():
            ft = v['filetype']
            size = v['size']
            add = False
            if filetype == 11 and ft == 11:
               obsid, second, vcs, part = split_raw_voltage(f)
               add = True
            elif filetype == 12 and ft == 12:
                obsid, second, chan = split_raw_recombined(f)
                add = True
            elif filetype == 15 and ft == 15:
               obsid, second = split_ics(f)
               add = True
            elif filetype == 16:
               if ft == 16:
                  obsid, second = split_combined(f)
                  add = True
               elif ft == 15:
                  obsid, second = split_ics(f)
                  add = True

            if add and second >= timefrom and second <= (timefrom + duration):
                keymap[f] = size
                  
      else:
         for f, v in files.iteritems():
            ft = v['filetype']
            size = v['size']
            if filetype == 11 and ft == 11:
               keymap[f] = size
            elif filetype == 12 and ft == 12:
               keymap[f] = size
            elif filetype == 15 and ft == 15:
               keymap[f] = size
            elif filetype == 16 and (ft == 15 or ft == 16):
               keymap[f] = size

      return keymap

   finally:
      if response:
         response.close()


def check_complete(filename, size, dir):
    path = dir + filename

    # check the file exists
    if os.path.isfile(path) is True:
        #check the filesize matches
        filesize = os.stat(path).st_size
        if filesize == int(size):
            return True
    return False


def download_queue_thread(queue):
   while not queue.empty():
      try:
         item = queue.get(timeout = 1)
         download_worker(*item)
      except Empty:
         return
      
def download_worker(url, filename, size, out, bufsize, prestage):

    u = None

    try:
        file_starting(filename)

        request = urllib2.Request(url)
        base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
        request.add_header('Authorization', 'Basic %s' % base64string)
        request.add_header('prestagefilelist', prestage)

        u = urllib2.urlopen(request)
        u.fp.bufsize = bufsize

        file_size = int(u.headers['Content-Length'])
        file_size_dl = 0

        with open(out + filename, 'wb') as f:
           while True:
               buff = u.read(bufsize)
               if not buff:
                 break
   
               f.write(buff)
               file_size_dl += len(buff)

        if file_size_dl != file_size:
          raise Exception('size mismatch %s %s' % str(file_size), str(file_size_dl))

        file_complete(filename)

    except urllib2.HTTPError as e:
        file_error('%s [ERROR] %s %s' % (time.strftime('%c'), filename, str(e.read()) ))

    except urllib2.URLError as urlerror:
        if hasattr(urlerror, 'reason'):
            file_error('%s [ERROR] %s %s' % (time.strftime('%c'), filename, str(urlerror.reason) ))
        else:
            file_error('%s [ERROR] %s %s' % (time.strftime('%c'), filename, str(urlerror) ))

    except Exception as exp:
        file_error('%s [ERROR] %s %s' % (time.strftime('%c'), filename, str(exp) ))

    finally:
        if u:
            u.close()


def main():
   global COMPLETE
   global TOTAL_FILES
   global ERRORS

   parser = OptionParser(usage='usage: %prog [options]', version='%prog 1.0')
   parser.add_option('--obs', action='store', dest='obs', help='Observation ID')
   parser.add_option('--type', default = 16, action='store', type = 'int',
                       dest='filetype', help='Voltage data type (Raw = 11, ICS Only = 15, Recombined and ICS = 16)')
   parser.add_option('--from', action='store', type = 'int', dest='timefrom',
                       help='Time from (taken from filename)')
   parser.add_option('--duration', default = 0, type = 'int', dest='duration',
                       help='Duration (seconds)')
   parser.add_option('--ngas',  default='fe4.pawsey.org.au:7790', action='store',
                       dest='ngashost', help='NGAS server (default: fe4.pawsey.org.au:7790)')
   parser.add_option('--dir', default= './', action='store', dest='out',
                       help='Output directory (default: ./')
   parser.add_option('--parallel', default='6', action='store', dest='td',
                       help='Number of simultaneous downloads (default: 6)')
   
   bufsize = 65536
   (options, args) = parser.parse_args()
   
   if options.ngashost == None:
       print('NGAS host not defined')
       sys.exit(-1)
   
   if options.obs == None:
       print('Observation ID is empty')
       sys.exit(-1)
   
   if options.filetype == None:
       print('File type not specified')
       sys.exit(-1)
   
   #if options.timefrom == None:
   #    print('Time from not specified')
    #   sys.exit(-1)
   
   if options.timefrom != None and options.duration != None:
       if options.duration < 0:
          print('Duration must not be negative')
          sys.exit(-1)
   
   numdownload = int(options.td)
   
   if numdownload <= 0 or numdownload > 12:
       print('Number of simultaneous downloads must be > 0 and <= 12')
       sys.exit(-1)
   
   print('%s [INFO] Finding observation %s' % (time.strftime('%c'), options.obs))
   
   fileresult = query_observation(options.obs, 'mwa-metadata01.pawsey.org.au',
                                   options.filetype, options.timefrom, options.duration)
   if len(fileresult) <= 0:
       print('%s [INFO] No files found for observation %s and file type %s' % (time.strftime('%c'),
                                                                               options.obs,
                                                                               int(options.filetype)))
       sys.exit(1)
   
   print('%s [INFO] Found %s files' % (time.strftime('%c'), str(len(fileresult))))

   if len(fileresult) > 12000:
       print('%s [INFO] File limit exceeded 12000, please stagger your download' % (time.strftime('%c')))
       sys.exit(1)
   
   # advise that we want to prestage all the files
   filelist = []
   for key, value in fileresult.iteritems():
      filelist.append(key)
   
   prestage_files = json.dumps(filelist)
   
   if options.out == None or len(options.out) == 0:
       options.out = './' + options.out + '/'
   
   # check we have a forward slash before file
   if options.out[len(options.out)-1] != '/':
        options.out += '/'
   
   dir = options.out
   if not os.path.exists(dir):
       os.makedirs(dir)
   
   TOTAL_FILES = len(fileresult)
   download_queue = Queue()
   
   for filename, filesize in sorted(fileresult.items()):
       url = 'http://%s/RETRIEVE?file_id=%s' % (options.ngashost, filename)
       if not check_complete(filename, int(filesize), dir):
           download_queue.put((url, filename, filesize, dir, bufsize, prestage_files))
           continue
       file_complete(filename)
   
   threads = []
   for t in xrange(numdownload):
      t = threading.Thread(target = download_queue_thread, args = (download_queue,))
      t.setDaemon(True)
      threads.append(t)
      t.start()
      
   for t in threads:
      while t.isAlive():
         t.join(timeout = 0.25)
               
   print('%s [INFO] File Transfer Complete.' % (time.strftime('%c')))
   
   if ERRORS:
       print('%s [INFO] File Transfer Error Summary:' % (time.strftime('%c')))
       for i in ERRORS:
           print(i)
       raise Exception()
   else:
       print('%s [INFO] File Transfer Success.' % (time.strftime('%c')))


if __name__ == '__main__':
    try:
        main()
        os._exit(0)

    except KeyboardInterrupt as k:
        print('Interrupted, shutting down')
        os._exit(2)

    except Exception as e:
        print(e)
        os._exit(3)
