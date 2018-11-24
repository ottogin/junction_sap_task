# need pip install deepaffects
#in case of trubles:
# Download and extract the files @sbraz mentioned previously to ~/Downloads: http://mediaarea.net/download/binary/libmediainfo0/0.7.84/MediaInfo_DLL_0.7.84_Mac_i386+x86_64.tar.bz2
# Then copy the file libmediainfo.0.dylib to /usr/local/lib

from __future__ import print_function
import time
import deepaffects
from deepaffects.rest import ApiException
from pprint import pprint
import requests
import json

deepaffects.configuration.api_key['apikey'] = 'MfKtVsGBRnYrjpN0LUO8lHAPwwOpHKYD'

#deleat person
def del_person(identifier):
    URL = 'https://proxy.api.deepaffects.com/audio/generic/api/v1/sync/diarization/delete'
    payload = {"speakerId": identifier}

    headers = {
        'content-type': 'application/json'
    }
    params = {
        'apikey': deepaffects.configuration.api_key['apikey']
    }

    r = requests.post(URL, data=json.dumps(payload), headers = headers, params = params)
    return r

#get all person
def get_all_users():
    """
        RETURN:
            list of users ids in the system
    """
    URL = 'https://proxy.api.deepaffects.com/audio/generic/api/v1/sync/diarization/get_enrolled_speakers'
    params = {
        'apikey': deepaffects.configuration.api_key['apikey']
    }

    r = requests.get(URL, params = params)
    all_users = json.loads(r.content)['enrolled_speaker_ids']
    return [x['speaker_id'] for x in all_users]

def define_emotion_from_audio(path_to_audio):
    body = deepaffects.Audio.from_file(file_name=path_to_audio)

    URL = 'https://proxy.api.deepaffects.com/audio/generic/api/v2/sync/recognise_emotion'
    payload = {"content": body.content, 
               "sampleRate": body.sample_rate, 
               "encoding": body.encoding, 
               "languageCode": body.language_code}

    headers = {
        'content-type': 'application/json'
    }
    params = {
        'apikey': deepaffects.configuration.api_key['apikey']
    }

    r = requests.post(URL, data=json.dumps(payload), headers = headers, params = params)
    all_segments = json.loads(r.content)
    
    all_duration = 0
    max_dur = 0
    spoken_emotion = ''
    for seg in all_segments:
        cur_dur = seg['end'] - seg['start']
        all_duration += cur_dur
        if cur_dur > max_dur:
            max_dur = cur_dur
            spoken_emotion = seg['emotion']
    confidence = max_dur/all_duration
    return spoken_emotion, confidence, all_segments

def define_emotion_from_text(text):
    URL = 'https://proxy.api.deepaffects.com/text/generic/api/latest/sync/text_recognise_emotion'
    payload = {
      "content": text
    }

    headers = {
        'content-type': 'application/json'
    }
    params = {
        'apikey': deepaffects.configuration.api_key['apikey']
    }

    r = requests.post(URL, data=json.dumps(payload), headers = headers, params = params)

    r.content
    d = json.loads(r.content)

    max_val = 0
    mood = ''
    for i,j in d['response'].items():
        if j > max_val:
            max_val = j
            mood = i
    return mood

#adding person
def add_user(paths_to_3_audios, identifier):
    """
    Adds user. 
    Example: add_user([PATH_1, PATH_2, PATH_3], 'user_id_1')
    
    RETURN:
        list of requests statuses
    """
    responds = []
    for path_to_audio in paths_to_3_audios:
        body = deepaffects.Audio.from_file(file_name=path_to_audio)
        URL = 'https://proxy.api.deepaffects.com/audio/generic/api/v1/sync/diarization/enroll'
        payload = {"content": body.content, 
                   "sampleRate": body.sample_rate, 
                   "encoding": body.encoding, 
                   "languageCode": body.language_code, 
                   "speakerId": identifier}

        headers = {
            'content-type': 'application/json'
        }
        params = {
            'apikey': deepaffects.configuration.api_key['apikey']
        }

        r = requests.post(URL, data=json.dumps(payload), headers = headers, params = params)
        responds.append(r)
        
    for path_to_audio in paths_to_3_audios[:1]:
        body = deepaffects.Audio.from_file(file_name=path_to_audio)
        URL = 'https://proxy.api.deepaffects.com/audio/generic/api/v1/sync/diarization/enroll'
        payload = {"content": body.content, 
                   "sampleRate": body.sample_rate, 
                   "encoding": body.encoding, 
                   "languageCode": body.language_code, 
                   "speakerId": identifier}

        headers = {
            'content-type': 'application/json'
        }
        params = {
            'apikey': deepaffects.configuration.api_key['apikey']
        }

        r = requests.post(URL, data=json.dumps(payload), headers = headers, params = params)
        responds.append(r)
    return responds

def identify(path_to_audio, users_ids_to_identify = get_all_users()):
    """
    Args:
        path_to_audio: path to the audio to identify
        users_ids_to_identify: we want to identify one of the these users
    Return:
        identified user id, confidence and list of all segments
        
    """
    body = deepaffects.Audio.from_file(file_name=path_to_audio)

    URL = 'https://proxy.api.deepaffects.com/audio/generic/api/v1/sync/diarization/identify'
    payload = {"content": body.content, 
               "sampleRate": body.sample_rate, 
               "encoding": body.encoding, 
               "languageCode": body.language_code, 
               "speakerIds" : users_ids_to_identify}

    headers = {
        'content-type': 'application/json'
    }
    params = {
        'apikey': deepaffects.configuration.api_key['apikey']
    }

    r = requests.post(URL, data=json.dumps(payload), headers = headers, params = params)
    d = json.loads(r.content)
    all_segments = d['segments']
    
    all_duration = 0
    max_dur = 0
    spoken_user = ''
    for seg in all_segments:
        cur_dur = seg['end'] - seg['start']
        all_duration += cur_dur
        if cur_dur > max_dur:
            max_dur = cur_dur
            spoken_user = seg['speaker_id']
    
    confidence = max_dur/all_duration
    
    return spoken_user, confidence, all_segments

# set users in the system
if __name__ == '__main__':
    usersid2name = {'user1':'Artem', 'user2':'Nikita', 'user3':'Misha', 'user4':'Ahan', 'user5': 'Venya',
                   'UserNotIdentified': 'UserNotIdentified'}
    
#     status = add_user(['./enrol_voices/Artem1.m4a', 
#                        './enrol_voices/Artem2.m4a', 
#                        './enrol_voices/Artem3.m4a'], 
#                        'user1')
#     status = add_user(['./enrol_voices/Nikita1.m4a', 
#                        './enrol_voices/Nikita2.m4a', 
#                        './enrol_voices/Nikita3.m4a'], 
#                        'user2')
#     status = add_user(['./enrol_voices/Misha1.m4a', 
#                        './enrol_voices/Misha2.m4a', 
#                        './enrol_voices/Misha3.m4a'], 
#                        'user3')
#     status = add_user(['./enrol_voices/Ahan1.m4a', 
#                        './enrol_voices/Ahan2.m4a', 
#                        './enrol_voices/Ahan3.m4a'], 
#                        'user4')
#     status = add_user(['./enrol_voices/Venya1.m4a', 
#                        './enrol_voices/Venya2.m4a', 
#                        './enrol_voices/Venya3.m4a'], 
#                        'user5')
    
    all_users = get_all_users()
    print(all_users)
    
    #testing
    ide_user, conf, all_seg = identify('./voice_samples/Tema2.m4a', users_ids_to_identify = all_users)
    print(usersid2name[ide_user], conf)

    ide_user, conf,all_seg = identify('./voice_samples/Ahan3.m4a', users_ids_to_identify = ['user4'])
    print(usersid2name[ide_user], conf)

    ide_user, conf,all_seg = identify('./voice_samples/Nikita2.m4a', users_ids_to_identify = all_users)
    print(usersid2name[ide_user], conf)

    ide_user, conf,all_seg = identify('./voice_samples/Nikita2.m4a', users_ids_to_identify = ['user2'])
    print(usersid2name[ide_user], conf, all_seg)

    ide_user, conf,all_seg = identify('./voice_samples/Nikita2.m4a', users_ids_to_identify = ['user3'])
    print(usersid2name[ide_user], conf, all_seg)

    ide_user, conf,all_seg = identify('./voice_samples/mish_2.m4a', users_ids_to_identify = all_users)
    print(usersid2name[ide_user], conf)


