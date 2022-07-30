import os
import json
import glob
import uuid
import numpy as np
from datetime import datetime
from acedistance.helpers.load import loadConfig

configParser = loadConfig()
cache_dir = os.path.join(os.path.dirname(__file__), '..', configParser['PROGRAM']['CACHE_DIR'])
date_format_str = '%d-%m-%Y %H:%M:%S'


def isValid(cache):
    """ Checks if cache data is valid based on expiration date

    Args:
        cache (object): Cache object

    Returns:
        Boolean: The cached data is valid or not
    """

    expr_date = cache['expiration_date']
    now = datetime.now().strftime(date_format_str)
    is_valid = now < expr_date

    return is_valid


def checkCache(layout):
    """ Loads correct cache data if there is a valid one exported

    Args:
        layout (str): Name of the layout

    Returns:
        tuple(bool, dict): Returns whether a valid cache was found and the corresponding data
    """

    out_dir = os.path.join(cache_dir, layout)
    if not os.path.exists(out_dir):
        return False, None

    for filename in glob.glob(os.path.join(out_dir, '*.json')):  # only process .JSON files in folder.
        with open(filename, mode='r') as f:
            cache = json.load(f)

            if isValid(cache):
                cache['position'] = tuple(cache['position'])
                return True, cache

    return False, None


def saveCache(layout, position, name='', overwrite=False):
    """ Saves cache data

    Args:
        layout (str): Name of the corresponding layout
        position (np.array): Position of the ace hole
        name (str): Optional, name of the cache
        overwrite (bool): Optional, if cache exists already, should it be overwritten

    Returns:
        None
    """

    # First check if cache already exists
    cache_id = str(uuid.uuid4())
    cache_exists, cache = checkCache(layout)

    if cache_exists and not overwrite:
        return

    if cache_exists and overwrite:
        cache_id = cache['id']

    expiration_date_str = datetime.now().date().strftime('%d-%m-%Y') + ' ' + '23:59:59'
    cache = {
        'id': cache_id,
        'name': name,
        'layout': layout,
        'position': np.array(position).tolist(),
        'expiration_date': expiration_date_str
    }

    out_dir = os.path.join(cache_dir, layout)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    cache_file_path = os.path.join(out_dir, f'{cache_id}.json')
    with open(cache_file_path, 'w') as f:
        json.dump(cache, f)
