# -*- coding: utf8 -*-
import os
import urllib
import requests


def detection_find_calibrator(addr, auth, **kwargs):
    """
    Find calibrators used in a detection from a particular observation.
    
    Args:
        addr: hostname or ip address of database server.
        auth: tuple of username and password. 
        detection_obsid: observation id of a detection
    """
    path = '{0}/{1}/'.format(addr, 'detection_find_calibrator')
    r = requests.get(url=path,
                    auth=auth,
                    params=urllib.urlencode(kwargs))
    r.raise_for_status()
    return r.json()

def calibration_file_by_observation_id(addr, auth, **kwargs):
    """
    Return a calibration and its file based on observation id.

    Args:
        addr: hostname or ip address of database server.
        auth: tuple of username and password.
        obsid: observation id to search.
    """
    path = '{0}/{1}/'.format(addr, 'calibration_file_by_observation_id')
    r = requests.get(url=path,
                    auth=auth,
                    params=urllib.urlencode(kwargs))
    r.raise_for_status()
    return r.json()

def calibrator_list(addr, auth):
    """
    Return a list of the all the calibrators in the database.
    
    Args:
        addr: hostname or ip address of database server.
        auth: tuple of username and password. 
    """
    path = '{0}/{1}/'.format(addr, 'calibrator_list')
    r = requests.get(url=path, auth=auth)
    r.raise_for_status()
    return r.json()

def calibrator_get(addr, auth, **kwargs):
    """
    Get a specific calibrator.
    
    Args:
        addr: hostname or ip address of database server.
        auth: tuple of username and password.
        observationid: observation id of the calibrator.
        caltype: id of calibrator type (check database for type id)
    """
    path = '{0}/{1}/'.format(addr, 'calibrator_get')
    r = requests.get(url=path,
                     auth=auth,
                     params=urllib.urlencode(kwargs))
    r.raise_for_status()
    return r.json()

def calibrator_create(addr, auth, **kwargs):
    """
    Create a new calibrator.
    
    Args:
        addr: hostname or ip address of database server.
        auth: tuple of username and password.
        observationid: observation id of the calibrator.
        caltype: id of calibrator type
        notes: any notes regarding calibrator
    """
    path = '{0}/{1}/'.format(addr, 'calibrator_create')
    r = requests.post(url=path, auth=auth, data=kwargs)
    r.raise_for_status()
    return r.json()

def pulsar_list(addr, auth):
    """
    Return a list of the all the pulars in the database.
    
    Args:
        addr: hostname or ip address of database server.
        auth: tuple of username and password. 
    """
    path = '{0}/{1}/'.format(addr, 'pulsar_list')
    r = requests.get(url=path, auth=auth)
    r.raise_for_status()
    return r.json()

def pulsar_get(addr, auth, **kwargs):
    """
    Return a specified pulsar from the database.
    
    Args:
        addr: hostname or ip address of database server.
        auth: tuple of username and password.
        name: name of pulsar.
    """
    path = '{0}/{1}/'.format(addr, 'pulsar_get')
    r = requests.get(url=path,
                    auth=auth,
                    params=urllib.urlencode(kwargs))
    r.raise_for_status()
    return r.json()

def pulsar_create(addr, auth, **kwargs):
    """
    Create a new pulsar. 
    
    Args:
        addr: hostname or ip address of database server.
        auth: tuple of username and password.
        name: name of pulsar.
        ra: right ascension of pulsar. 
        dec: declination of pulsar. 
    Raises:
        Exception if pulsar already exists or there is an input error. 
    """
    path = '{0}/{1}/'.format(addr, 'pulsar_create')
    r = requests.post(url=path, auth=auth, data=kwargs)
    r.raise_for_status()
    return r.json()

def detection_list(addr, auth):
    """
    Return a list of the all the pulsar detection in the database.
    
    Args:
        addr: hostname or ip address of database server.
        auth: tuple of username and password. 
    """
    path = '{0}/{1}/'.format(addr, 'detection_list')
    r = requests.get(url=path, auth=auth)
    r.raise_for_status()
    return r.json()

def detection_get(addr, auth, **kwargs):
    """
    Return a specified pulsar detection from the database.
    
    Args:
        addr: hostname or ip address of database server.
        auth: tuple of username and password.
        observationid: observation id.
    """
    path = '{0}/{1}/'.format(addr, 'detection_get')
    r = requests.get(url=path,
                    auth=auth,
                    params=urllib.urlencode(kwargs))
    r.raise_for_status()
    return r.json()

def detection_update(addr, auth, **kwargs):
    """
    Update an extising detection. 
    observationid, pulsar and subband, coherent form a unique set per detection.

    Args:
        addr: hostname or ip address of database server.
        auth: tuple of username and password.
        observationid: observation id. 
        pulsar: name of pulsar (string). 
        subband: subband of detection.
        coherent: coherent data set (True), incoherent (False)
        observation_type: type of observation (1: Contiguous, 2: Picket Fence)
        calibrator: id of calibrator (or None).
        startcchan: start course channel (or None).
        stopcchan: stop course channel (or None). 
        flux: mJy (or None)
        flux_error: ±mJy (or None)
        width: ms (or None)
        width_error: ±ms (or None)
        scattering: s (or None)
        scattering_error: ±s (or None)
        dm: pc/cm³ (or None)
        dm_error: ±pc/cm³
        version: version number of client script used. (default 1)

    Raises:
        Exception if detection already exists or there is an input error.
    """
    path = '{0}/{1}/'.format(addr, 'detection_update')
    r = requests.post(url=path, auth=auth, data=kwargs)
    r.raise_for_status()
    return r.json()

def detection_create(addr, auth, **kwargs):
    """
    Create a new detection. 
    observationid, pulsar and subband, coherent form a unique set per detection.

    Args:
        addr: hostname or ip address of database server.
        auth: tuple of username and password.
        observationid: observation id. 
        pulsar: name of pulsar (string). 
        subband: subband of detection.
        coherent: coherent data set (True), incoherent (False)
        observation_type: type of observation (1: Contiguous, 2: Picket Fence)
        calibrator: id of calibrator (or None).
        startcchan: start course channel (or None).
        stopcchan: stop course channel (or None). 
        flux: mJy (or None)
        flux_error: ±mJy (or None)
        width: ms (or None)
        width_error: ±ms (or None)
        scattering: s (or None)
        scattering_error: ±s (or None)
        dm: pc/cm³ (or None)
        dm_error: ±pc/cm³
        version: version number of client script used. (default 1)

    Raises:
        Exception if detection already exists or there is an input error.
    """
    path = '{0}/{1}/'.format(addr, 'detection_create')
    r = requests.post(url=path, auth=auth, data=kwargs)
    r.raise_for_status()
    return r.json()

def detection_file_upload(addr, auth, **kwargs):
    """
    Upload a file against a detection.
    
    Args:
        addr: hostname or ip address of database server.
        auth: tuple of username and password.
        observationid: observation id.
        pulsar: name of pulsar. 
        subband: subband of detection.
        coherent: coherent observation.
        filetype: (1: Archive, 2: Timeseries, 3: Diagnostics, 4: Calibration Solution)
        filepath: full local path of the file to upload. 
    """
    path = '{0}/{1}/'.format(addr, 'detection_file_upload')
    filepath = kwargs.get('filepath', None)
    if not filepath:
        raise Exception('filepath not found')
    files = {'path': open(filepath, 'rb')}
    new_kwargs = {}
    for k, v in kwargs.iteritems():
        new_kwargs[k] = str(v)
    r = requests.post(url=path, auth=auth, files=files, headers=new_kwargs)
    r.raise_for_status()
    return r.json()

def detection_file_download(addr, auth, filename, outputpath):
    """
    Download a specific detection file. 
    
    Args:
        addr: hostname or ip address of database server.
        auth: tuple of username and password.
        filename: name of the file recorded in the database. 
        out_path: local path where to place file.
    Returns:
        full path of the downloaded file.
    Raises:
        Exception if there is a file error or file not found. 
    """
    path = '{0}/{1}/'.format(addr, 'detection_file_download')
    params = {'filename': filename}
    r = requests.get(url=path,
                    auth=auth,
                    params=urllib.urlencode(params),
                    stream=True)
    r.raise_for_status()

    try:
        os.makedirs(outputpath)
    except OSError:
        pass

    full_output_path = '{0}/{1}'.format(outputpath, filename)
    with open(full_output_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)

    return full_output_path


def calibrator_file_upload(addr, auth, **kwargs):
    """
    Upload a file against a calibrator.
    
    Args:
        addr: hostname or ip address of database server.
        auth: tuple of username and password.
        observationid: observation id.
        caltype: (check database for id)
        filepath: full local path of the file to upload. 
    """
    path = '{0}/{1}/'.format(addr, 'calibrator_file_upload')
    filepath = kwargs.get('filepath', None)
    if not filepath:
        raise Exception('filepath not found')
    files = {'path': open(filepath, 'rb')}
    new_kwargs = {}
    for k, v in kwargs.iteritems():
        new_kwargs[k] = str(v)
    r = requests.post(url=path, auth=auth, files=files, headers=new_kwargs)
    r.raise_for_status()
    return r.json()


def calibrator_file_download(addr, auth, filename, outputpath):
    """
    Download a specific calibration file. 
    
    Args:
        addr: hostname or ip address of database server.
        auth: tuple of username and password.
        filename: name of the file recorded in the database. 
        out_path: local path where to place file.
    Returns:
        full path of the downloaded file.
    Raises:
        Exception if there is a file error or file not found. 
    """
    path = '{0}/{1}/'.format(addr, 'calibrator_file_download')
    params = {'filename': filename}
    r = requests.get(url=path,
                    auth=auth,
                    params=urllib.urlencode(params),
                    stream=True)
    r.raise_for_status()

    try:
        os.makedirs(outputpath)
    except OSError:
        pass

    full_output_path = '{0}/{1}'.format(outputpath, filename)
    with open(full_output_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)

    return full_output_path

def psrcat(addr, auth, pulsar):
    """
    Return the pulsar details from psrcat.

    Args:
        pulsar: name of the pulsar.
    Returns:
        psrcat details as a python dict.
    Exception:
        pulsar not found or bad input.
    """
    path = '{0}/{1}/'.format(addr, 'psrcat')
    payload = {'name': pulsar, 'format': 'json'}
    r = requests.get(url=path,
                    auth=auth,
                    params=urllib.urlencode(payload))
    r.raise_for_status()
    return r.json()
