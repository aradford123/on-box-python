import requests

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

    url = SPARK_API + 'messages'
    HEADERS = {
        'authorization': token,
        'content-type': 'application/json'
    }
    payload = {'roomId': roomId, 'markdown': message}
    r = requests.request(
        'POST', url, json=payload, headers=HEADERS)
    r.raise_for_status()
