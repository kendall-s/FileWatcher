import os
from os import listdir
from os.path import isfile, join
import shutil
import hashlib
import json
import win32wnet

def read_in_parameters(file):
    """
    Read in the given parameters json file
    """

    with open(file) as params_file:
        params_file_json = json.load(params_file)
    return params_file_json


def create_wnet_connection(host_path, domain, username, password):
    """
    Creates the windows network share connection using the provided authentication, allows the application to gain access to the 
    files which are to be copied.
    """
    domain_username = domain + '\\' + username
    try:
        win32wnet.WNetAddConnection2(0, None, '\\\\' + host_path, None, domain_username, password)
    except Exception as err:
        if isinstance(err, win32wnet.error):
            if err.winerror == 1219:
                return {'outcome': 'cancel', 'message': 'Existing connection with different credentials. Cancel then reconnect.'}
        else:
            return {'outcome': 'error', 'message': f'The connection to the host ({host_path}) could not be made. Error: {err}'}
    return {'outcome': 'success', 'message': f'A connection to the host ({host_path}) has been established'}


def remove_wnet_connection(host_path):
    """
    Remove the windows network share after it is no longer needed
    """
    try:
        win32wnet.WNetCancelConnection2('\\\\'+ host_path, 0, 0)
    except Exception as e:
        return {'outcome': 'error', 'message': f'The connection to the host ({host_path}) could not be cancelled. Error: {e}'}

    return {'outcome': 'success', 'message': f'The host connection ({host_path}) has been cancelled'}

def check_for_files(path, name_contains, file_type):
    """
    Check in the given path if there is a file matching the contains and type
    """
    # Get files in path
    files = [f for f in listdir(path) if isfile(join(path, f))]
    files_with_ext = [f for f in files  if os.path.splitext(f)[1] == file_type]
    files_with_name = [f for f in files_with_ext if name_contains in f]

    return files_with_name

def copy_file(source, to):
    """
    Use the shutil function copy2 to copy the file and its metadata as is

    """
    try:
        shutil.copy2(source, to)
    except IOError as e:
        print(e)
        return {'outcome': 'error', 'message': f'Unable to copy file. {e}'}

    return {'outcome': 'success', 'message': 'File copied.'}

def make_checksum(file):
    """
    Generate and return MD5 hash of input file
    """
    with open(file, 'rb') as open_file:
        data = open_file.read()
        hash = hashlib.md5(data).hexdigest()
    return hash

def verify_checksums(source, dest):
    """
    Compare two checksums and return their equality
    """
    if source == dest:
        return True
    else:
        return False

def fmt_str_with_voyage_name(string, voyage):
    """
    Substitutes the voyage name in given string where ?voyage is specified
    """
    formatted_string = string.replace("?voyage", voyage)
    return formatted_string
