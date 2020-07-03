"""Robinhood.py: a collection of utilities for working with Robinhood's Private API """

#Standard libraries
import logging
import warnings

from enum import Enum

#External dependencies
from six.moves.urllib.parse import unquote  # pylint: disable=E0401
from six.moves.urllib.request import getproxies  # pylint: disable=E0401
from six.moves import input

import getpass
import requests
import json
import os
import dateutil
import time
import random
import hmac, base64, struct, hashlib

#Application-specific imports
import RobinhoodClient.exceptions as RH_exception
import RobinhoodClient.endpoints as endpoints

class Bounds(Enum):
    """Enum for bounds in `historicals` endpoint """

    REGULAR = 'regular'
    EXTENDED = 'extended'

class Transaction(Enum):
    """Enum for buy/sell orders """

    BUY = 'buy'
    SELL = 'sell'

class Robinhood:
  """Wrapper class for fetching/parsing Robinhood endpoints """

  session = None
  username = None
  password = None
  headers = None
  auth_token = None
  refresh_token = None
  device_token = None
  expire_time = None

  logger = logging.getLogger('Robinhood')
  logger.addHandler(logging.NullHandler())

  client_id = "c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS"

  ###########################################################################
  #                       Logging in and initializing
  ###########################################################################

  def __init__(self):
    self.session = requests.session()
    self.session.proxies = getproxies()
    self.headers = {
      "Accept": "*/*",
      "Accept-Encoding": "gzip, deflate",
      "Accept-Language": "en;q=1, fr;q=0.9, de;q=0.8, ja;q=0.7, nl;q=0.6, it;q=0.5",
      "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
      "X-Robinhood-API-Version": "1.0.0",
      "Connection": "keep-alive",
      "User-Agent": "Robinhood/823 (iPhone; iOS 7.1.2; Scale/2.00)"
    }
    self.session.headers = self.headers
    self.device_token = ""
    self.challenge_id = ""
    if "auth.secret" in os.listdir('.'):
      data = open("auth.secret", "r").read()
      auth_data = json.loads(data)
      if "auth_token" in auth_data:
        self.auth_token = auth_data['auth_token']
        self.device_token = auth_data['device_token']
        self.refresh_token = auth_data['refresh_token']

  def GenerateDeviceToken(self):
    rands = []
    for i in range(0,16):
      r = random.random()
      rand = 4294967296.0 * r
      rands.append((int(rand) >> ((3 & i) << 3)) & 255)

    hexa = []
    for i in range(0,256):
      hexa.append(str(hex(i+256)).lstrip("0x").rstrip("L")[1:])

    id = ""
    for i in range(0,16):
      id += hexa[rands[i]]

      if (i == 3) or (i == 5) or (i == 7) or (i == 9):
        id += "-"

    self.device_token = id

  def get_mfa_token(self, secret):
      intervals_no = int(time.time())//30
      key = base64.b32decode(secret, True)
      msg = struct.pack(">Q", intervals_no)
      h = hmac.new(key, msg, hashlib.sha1).digest()
      o = h[19] & 15
      h = '{0:06d}'.format((struct.unpack(">I", h[o:o+4])[0] & 0x7fffffff) % 1000000)
      return h

  def relogin_oauth2(self):
      '''
      (Re)login using the Oauth2 refresh token
      '''
      print("Token refreshed, relogging in")
      url = "https://api.robinhood.com/oauth2/token/"
      data = {
          "client_id": self.client_id,
          "auth_token": self.auth_token,
          "device_token": self.device_token,
          "grant_type": "refresh_token",
          "refresh_token": self.refresh_token,
          "scope": "internal",
          "expires_in": 86400,
      }
      res = self.session.post(url, data=data)
      data = res.json()

      if 'access_token' in data.keys() and 'refresh_token' in data.keys():
        print(data)
        self.auth_token = data['access_token']
        self.refresh_token = data['refresh_token']
        self.headers['Authorization'] = 'Bearer ' + self.auth_token
        return True

      # if res.status_code == 200:
      #     print("Successful relogin")
      #     res = json.loads(res.content)
      #     self.auth_token = res["access_token"]
      #     self.refresh_token = res["refresh_token"]
      #     #self.mfa_code       = res["mfa_code"]
      #     #self.scope          = res["scope"]
      # else:
      #     res = json.loads(res.content)
      #     print("Error while refreshing login")
      #     print(res['error'])

  def login(self,
            username,
            password,
            challenge_type = 'sms'):
      """Save and test login info for Robinhood accounts
      Args:
          username (str): username
          password (str): password
          qr_code (str): QR code that will be used to generate mfa_code (optional but recommended)
          To get QR code, set up 2FA in Security, get Authentication App, and click "Can't Scan It?"
      Returns:
          (bool): received valid auth token
      """
      self.username = username
      self.password = password

      if self.device_token == "":
          self.GenerateDeviceToken()

      payload = {
          'password': self.password,
          'username': self.username,
          'grant_type': 'password',
          'client_id': "c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS",
          'expires_in': '86400',
          'scope': 'internal',
          'device_token': self.device_token,
          'challenge_type': challenge_type
      }

      try:
          res = self.session.post(endpoints.login(), data=payload, timeout=15)
          res_data = res.json()

          if 'access_token' in res_data.keys() and 'refresh_token' in res_data.keys():
              print(res_data)
              self.auth_token = res_data['access_token']
              self.refresh_token = res_data['refresh_token']
              self.headers['Authorization'] = 'Bearer ' + self.auth_token
              return True

          if self.challenge_id == "" and "challenge" in res_data.keys():
              self.challenge_id = res_data["challenge"]["id"]

          self.headers["X-ROBINHOOD-CHALLENGE-RESPONSE-ID"] = self.challenge_id #has to add this to stay logged in
          sms_challenge_endpoint = "https://api.robinhood.com/challenge/{}/respond/".format(self.challenge_id)
          
          print("No 2FA Given")
          print("Enter code:")
          self.sms_code = input()
          challenge_res = {"response":self.sms_code}
          
          res2 = self.session.post(sms_challenge_endpoint, data=challenge_res, timeout=15)
          res2.raise_for_status()
          #gets access token for final response to stay logged in
          res3 = self.session.post(endpoints.login(), data=payload, timeout=15)
          res3.raise_for_status()
          data = res3.json()
          print(data)

          if 'access_token' in data.keys() and 'refresh_token' in data.keys():
              self.auth_token = data['access_token']
              self.refresh_token = data['refresh_token']
              self.headers['Authorization'] = 'Bearer ' + self.auth_token
              self.expire_time = data['expires_in']
              return True

      except requests.exceptions.HTTPError:
          raise RH_exception.LoginFailed()

      return False
