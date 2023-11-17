import pyaudio
import pyaudio_hack

def get_audio_device_info_list():
    pa = pyaudio_hack.PyAudioHack()
    device_info_list = pa.get_device_info_list_hack()
    device_info_list = filter(lambda x: x['maxOutputChannels'] > 0, device_info_list)
    device_info_list = filter(lambda x: x['hostApi'] == pyaudio.paMME, device_info_list)
    device_info_list = list(device_info_list)
    return device_info_list

audio_device_info_list = get_audio_device_info_list()
for device_info in audio_device_info_list:
    print(f'md5={device_info["md5"]}')
    print(device_info)
