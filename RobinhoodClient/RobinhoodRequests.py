import requests
import RobinhoodClient.endpoints as endpoints
import RobinhoodClient.Constants as constants

from six.moves.urllib.request import getproxies
from six.moves import input

def get_login_tokens(username, password, device_token):
  session = get_session()
  payload = get_payload(username, password, device_token)

  try:
    response_json = request_login_data_json(session, payload)

    if not login_successful(response_json):
      challenge_id = response_json["challenge"]["id"]
      
      sms_code = get_sms_code()
      request_login_challenge(session, sms_code, challenge_id)

      response_json = request_login_data_json(session, payload)

      return get_login_response_data(response_json, challenge_id)

    return get_login_response_data(response_json)

  except requests.exceptions.HTTPError:
    print("ERROR: Login failed")
    raise requests.exceptions.HTTPError
  except Exception as e:
    print("Unknown Error")
    raise e

def get_session():
  session = requests.session()
  session.proxies = getproxies()
  session.headers = {
      "Accept": "*/*",
      "Accept-Encoding": "gzip, deflate",
      "Accept-Language": "en;q=1, fr;q=0.9, de;q=0.8, ja;q=0.7, nl;q=0.6, it;q=0.5",
      "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
      "X-Robinhood-API-Version": "1.0.0",
      "Connection": "keep-alive",
      "User-Agent": "Robinhood/823 (iPhone; iOS 7.1.2; Scale/2.00)"
  }
  return session

def get_payload(username, password, device_token):
  return {
    'password': password,
    'username': username,
    'grant_type': 'password',
    'client_id': "c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS",
    'expires_in': '86400',
    'scope': 'internal',
    'device_token': device_token,
    'challenge_type': 'sms'
  }

def request_login_data_json(session, payload):
  response = session.post(endpoints.login(), data=payload, timeout=constants.TIMEOUT)
  response_json = response.json()
  return response_json
  
def login_successful(response_json):
  return 'access_token' in response_json.keys() and 'refresh_token' in response_json.keys()

def get_login_response_data(response_json, challenge_id=None):
  tokens = {}

  tokens['access_token'] = response_json['access_token']
  tokens['refresh_token'] = response_json['refresh_token']
  tokens['expires_in'] = response_json['expires_in']
  tokens['challenge_id'] = challenge_id

  return tokens

def request_login_challenge(session, sms_code, challenge_id):
  challenge_res = {"response": sms_code}
  sms_challenge_endpoint = endpoints.login_challenge(challenge_id)

  session.headers["X-ROBINHOOD-CHALLENGE-RESPONSE-ID"] = challenge_id

  res = session.post(sms_challenge_endpoint, data=challenge_res, timeout=15)
  res.raise_for_status()
  

def get_sms_code():
  print("No 2FA Given")
  print("Enter code:")
  return input()