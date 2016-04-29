import os
import urllib
import requests

def pulsar_list(addr, auth):
    path = 'https://{0}/{1}/'.format(addr, 'pulsar_list')
    r = requests.post(url = path, auth = auth)
    r.raise_for_status()
    return r.json()

def pulsar_get(addr, auth, name):
    path = 'https://{0}/{1}/'.format(addr, 'pulsar_get')
    payload = {'name': name}
    r = requests.post(url = path, auth = auth, data = payload)
    r.raise_for_status()
    return r.json()

def pulsar_create(addr, auth, name, ra, dec):
    path = 'https://{0}/{1}/'.format(addr, 'pulsar_create')
    payload = {'name': name, 'ra': ra, 'dec': dec}
    r = requests.post(url = path, auth = auth, data = payload)
    r.raise_for_status()
    return r.json()

def observation_list(addr, auth):
    path = 'https://{0}/{1}/'.format(addr, 'observation_list')
    r = requests.post(url = path, auth = auth)
    r.raise_for_status()
    return r.json()

def observation_get(addr, auth, obsid):
    path = 'https://{0}/{1}/'.format(addr, 'observation_get')
    payload = {'observationid': obsid}
    r = requests.post(url = path, auth = auth, data = payload)
    r.raise_for_status()
    return r.json()

def observation_create(addr, auth, obsid, pulsar, subband, obstype,
                       startcchan = None, stopcchan = None, flux = None,
                       flux_error = None, width = None, width_error = None,
                       scattering = None, scattering_error = None,
                       dm = None, dm_error = None):
    path = 'https://{0}/{1}/'.format(addr, 'observation_create')
    payload = {'observationid': obsid, 'pulsar': pulsar, 'subband': subband,
                'observationtype': obstype, 'startcchan': startcchan, 'stopcchan': stopcchan,
                'flux': flux, 'flux_error': flux_error,
                'width': width, 'width_error': width_error,
                'scattering': scattering, 'scattering_error': scattering_error,
                'dm': dm, 'dm_error': dm_error}
    r = requests.post(url = path, auth = auth, data = payload)
    r.raise_for_status()
    return r.json()

def pulsar_file_upload(addr, auth, obsid, pulsar, subband, filetype, filepath):
    path = 'https://{0}/{1}/'.format(addr, 'pulsar_file_upload')
    headers = {'obsid': obsid, 'pulsar': pulsar, 'subband': subband,
                'filetype': filetype}
    files = {'path': open(filepath, 'rb')}
    r = requests.post(url = path, auth = auth, files = files, headers = headers)
    r.raise_for_status()
    return r.json()

def pulsar_file_download(addr, auth, filename, output_path):
    path = 'https://{0}/{1}/'.format(addr, 'pulsar_file_download')
    params = {'filename': filename}
    r = requests.get(url = path,
                        auth = auth,
                        params = urllib.urlencode(params),
                        stream = True)
    r.raise_for_status()

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    full_output_path = '{0}/{1}'.format(output_path, filename)
    with open(full_output_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size = 1024):
            if chunk:
                f.write(chunk)

    return full_output_path
