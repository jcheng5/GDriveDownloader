# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Command-line skeleton application for Drive API.
Usage:
  $ python sample.py

You can also get help on all the command-line flags the program understands
by running:

  $ python sample.py --help

"""

import argparse
import httplib2
import os
import re
import sys

from apiclient import discovery
from oauth2client import file
from oauth2client import client
from oauth2client import tools

# Parser for command-line arguments.
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[tools.argparser])


# CLIENT_SECRETS is name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret. You can see the Client ID
# and Client secret on the APIs page in the Cloud Console:
# <https://cloud.google.com/console#/project/751827116087/apiui>
CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')

# Set up a Flow object to be used for authentication.
# Add one or more of the following scopes. PLEASE ONLY ADD THE SCOPES YOU
# NEED. For more information on using scopes please see
# <https://developers.google.com/+/best-practices>.
FLOW = client.flow_from_clientsecrets(CLIENT_SECRETS,
  scope=[
      #'https://www.googleapis.com/auth/drive',
      #'https://www.googleapis.com/auth/drive.appdata',
      #'https://www.googleapis.com/auth/drive.apps.readonly',
      #'https://www.googleapis.com/auth/drive.file',
      #'https://www.googleapis.com/auth/drive.metadata.readonly',
      'https://www.googleapis.com/auth/drive.readonly',
      #'https://www.googleapis.com/auth/drive.scripts',
    ],
    message=tools.message_if_missing(CLIENT_SECRETS))


def main(argv):
  # Parse the command-line flags.
  flags = parser.parse_args(argv[1:])

  # If the credentials don't exist or are invalid run through the native client
  # flow. The Storage object will ensure that if successful the good
  # credentials will get written back to the file.
  storage = file.Storage('sample.dat')
  credentials = storage.get()
  if credentials is None or credentials.invalid:
    credentials = tools.run_flow(FLOW, storage, flags)

  # Create an httplib2.Http object to handle our HTTP requests and authorize it
  # with our good Credentials.
  http = httplib2.Http()
  http = credentials.authorize(http)

  # Construct the service object for the interacting with the Drive API.
  drive = discovery.build('drive', 'v2', http=http)

  try:
    files = drive.files()
    request = files.list(q="'root' in parents", fields="items/title")
    #while ( request != None ):
    #  fileData = request.execute()
    #  for item in fileData['items']:
    #    print item['title']
    #  request = files.list_next(request, fileData)
    print ls(drive, '/*')

  except client.AccessTokenRefreshError:
    print ("The credentials have been revoked or expired, please re-run"
      "the application to re-authorize")

def ls(drive, path, base = "root"):
  pathParts = [x for x in path.split("/") if x != ""]
  if len(pathParts) == 0:
    # We're already there
    return get_by_id(drive, base)
  elif len(pathParts) == 1:
    # The last part can be a name or glob
    return get_by_name(drive, pathParts[0], base, True)
  else:
    # Navigate and recurse
    name = pathParts[0]
    del pathParts[0]
    folders = get_by_name(drive, name, base, False)
    if len(folders) == 0:
      return []
    folder = folders[0]
    if folder['mimeType'] != "application/vnd.google-apps.folder":
      return []
    return ls(drive, "/".join(pathParts), folder['id'])

def get_by_name(drive, name, base = "root", allowGlob = False):
  q = "'%s' in parents" % base
  if (not allowGlob) or name.find("*") < 0:
    q += " and title = '%s'" % name.replace("'", r"\'")
    pattern = "^" + re.escape(name) + "$"
  else:
    pattern = "^" + ".*".join([re.escape(x) for x in name.split("*")]) + "$"
  items = []
  request = drive.files().list(q = q)
  while ( request != None ):
    response = request.execute()
    items = items + response['items']
    request = drive.files().list_next(request, response)
  return [x for x in items if re.match(pattern, x['title']) != None]

def get_by_id(drive, id):
  request = drive.files().get(fileId = id)
  return request.execute()

# For more information on the Drive API you can visit:
#
#   https://developers.google.com/drive/
#
# For more information on the Drive API Python library surface you
# can visit:
#
#   https://developers.google.com/resources/api-libraries/documentation/drive/v2/python/latest/
#
# For information on the Python Client Library visit:
#
#   https://developers.google.com/api-client-library/python/start/get_started
if __name__ == '__main__':
  main(sys.argv)
