# based on pyaudio 0.2.13

import base64
import copy
import hashlib
import json
import locale
import pyaudio

pa = pyaudio.pa

class PyAudioHack(pyaudio.PyAudio):

    def get_device_info_by_index_hack(self, device_index):
        """Returns the device parameters for device specified in `device_index`
        as a dictionary. The keys of the dictionary mirror the data fields of
        PortAudio's ``PaDeviceInfo`` structure.

        :param device_index: The device index
        :raises IOError: Invalid `device_index`.
        :rtype: dict
        """
        return self._make_device_info_dictionary_hack(
            device_index,
            pa.get_device_info(device_index))

    def _make_device_info_dictionary_hack(self, index, device_info):
        """Creates a dictionary like PortAudio's ``PaDeviceInfo`` structure.

        :rtype: dict
        """
        device_name = device_info.name

        # Attempt to decode device_name. If we fail to decode, return the raw
        # bytes and let the caller deal with the encoding.
        os_encoding = locale.getpreferredencoding(do_setlocale=False)
        for codec in [os_encoding, "utf-8"]:
            try:
                device_name = device_name.decode(codec)
                break
            except:
                pass

        device_name_bytes = device_info.name
        device_name_bytes_base64 = base64.b64encode(device_name_bytes).decode('utf-8')
        device_name_utf8 = device_name_bytes.decode('utf-8')

        ret = {'index': index,
                'structVersion': device_info.structVersion,
                'name': device_name,
                'hostApi': device_info.hostApi,
                'hostApiName': HOST_API_TYPE_TO_NAME_DICT.get(device_info.hostApi, None),
                'maxInputChannels': device_info.maxInputChannels,
                'maxOutputChannels': device_info.maxOutputChannels,
                'defaultLowInputLatency':
                device_info.defaultLowInputLatency,
                'defaultLowOutputLatency':
                device_info.defaultLowOutputLatency,
                'defaultHighInputLatency':
                device_info.defaultHighInputLatency,
                'defaultHighOutputLatency':
                device_info.defaultHighOutputLatency,
                'defaultSampleRate':
                device_info.defaultSampleRate,
                'name_bytes_base64':
                device_name_bytes_base64,
                'name_utf8':
                device_name_utf8}
        
        ret0 = copy.deepcopy(ret)
        ret0_json = json.dumps(ret0, sort_keys=True)
        ret0_json_md5 = hashlib.md5(ret0_json.encode('utf-8')).hexdigest()
        ret['md5'] = ret0_json_md5

        return ret

    def get_device_info_list_hack(self):
        device_count = self.get_device_count()
        ret_list = range(device_count)
        ret_list = map(self.get_device_info_by_index_hack, ret_list)
        ret_list = list(ret_list)
        return ret_list

    def get_device_info_by_md5_hack(self, md5):
        device_info_list = self.get_device_info_list_hack()
        device_info_list = filter(lambda x: x['md5'] == md5, device_info_list)
        device_info_list = list(device_info_list)
        if len(device_info_list) == 0:
            return None
        elif len(device_info_list) == 1:
            return device_info_list[0]
        else:
            raise Exception('md5 collision')

HOST_API_TYPE_TO_NAME_DICT = {
    pa.paInDevelopment: 'InDevelopment',
    pa.paDirectSound: 'DirectSound',
    pa.paMME: 'MME',
    pa.paASIO: 'ASIO',
    pa.paSoundManager: 'SoundManager',
    pa.paCoreAudio: 'CoreAudio',
    pa.paOSS: 'OSS',
    pa.paALSA: 'ALSA',
    pa.paAL: 'AL',
    pa.paBeOS: 'BeOS',
    pa.paWDMKS: 'WDMKS',
    pa.paJACK: 'JACK',
    pa.paWASAPI: 'WASAPI',
    pa.paNoDevice : 'NoDevice',
}
