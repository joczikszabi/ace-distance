import os
import shutil
from random import randint
from acedistance.helpers.load import loadConfig

files_to_release = [
    'estimate_distance.py',
    'refresh_cache.py',
    'setup.sh',
    'README.md',
    'environment.yml',
    'estimate_distance.py',
    os.path.join('acedistance', '__init__.py'),
    os.path.join('acedistance', 'main', '__init__.py'),
    os.path.join('acedistance', 'main', 'AceDistance.py'),
    os.path.join('acedistance', 'main', 'DistanceEstimation.py'),
    os.path.join('acedistance', 'main', 'ObjectDetection.py'),
    os.path.join('acedistance', 'main', 'Grid.py'),
    os.path.join('acedistance', 'main', 'constrains.py'),
    os.path.join('acedistance', 'config', 'config.ini')
]

directories_to_release = [
    'demo',
    os.path.join('acedistance', 'layouts'),
    os.path.join('acedistance', 'helpers')
]


def deploy():
    """
    Creates a release version of the ace-distance module which is a minified version of the repository containing
    only the necessary files to run the script.
    """

    configParser = loadConfig()

    # Set deployment meta data
    PACKAGE_NAME = 'acedistance'
    DEPLOY_VERSION = configParser['PROGRAM']['VERSION']
    DEPLOY_DATE = configParser['PROGRAM']['RELEASE_DATE']
    DEPLOY_SUFFIX = randint(1000, 9999)
    DEPLOY_DIR = f'{PACKAGE_NAME}_{DEPLOY_VERSION}_{DEPLOY_DATE}_{DEPLOY_SUFFIX}'

    # Copy necessary files to the release folder
    copy_files(files_to_release, DEPLOY_DIR)
    copy_directories(directories_to_release, DEPLOY_DIR)

    # Zip folder
    shutil.make_archive(f'{DEPLOY_DIR}', 'zip', DEPLOY_DIR)


def copy_files(files, release_folder):
    """
    Copy specified files to the release folder

    Args:
        files (list(str))): List of files to copy
        release_folder (str): Path to the release folder
    """

    for filename in files:
        filename_release = os.path.join(release_folder, filename)

        if not os.path.exists(os.path.dirname(filename_release)):
            os.makedirs(os.path.dirname(filename_release))

        shutil.copyfile(filename, filename_release)


def copy_directories(directories, release_folder):
    """
    Copy specified directories to the release folder

    Args:
        directories (list(str))): List of directories to copy
        release_folder (str): Path to the release folder
    """

    for dirname in directories:
        dirname_release = os.path.join(release_folder, dirname)
        shutil.copytree(dirname, dirname_release)


if __name__ == "__main__":
    deploy()
