import requests
from cli import cli
SPARK_API='https://api.ciscospark.com/v1/'


def getRoomId(roomName, token):
    '''
    finds a roomId from the name.  Raises exceptions if the REST API call fails or the room is not found
    :param roomName:
    :param token:
    :return:
    '''

    url = SPARK_API + 'rooms'
    HEADERS = {
        'authorization': token,
        'content-type': 'application/json'
    }

    r = requests.request('GET', url, headers=HEADERS)
    r.raise_for_status()


    room_id = None
    for room in r.json()['items']:
        if room['title'] == roomName:
            room_id = room['id']
            break
    if room_id is None:
        raise ValueError("no spark room {} found".format(roomName))
    return room_id

def postMessage(message, roomId, token):
    try:
        hostname = cli("show run | inc hostname").split()[1]
    except IndexError:
        raise ValueError("Cannot get device hostname")

    url = SPARK_API + 'messages'
    HEADERS = {
        'authorization': token,
        'content-type': 'application/json'
    }
    payload = {'roomId': roomId, 'markdown': '{host}: {mess}'.format(host=hostname, mess=message)}
    print payload
    r = requests.request(
        'POST', url, json=payload, headers=HEADERS)
    r.raise_for_status()
