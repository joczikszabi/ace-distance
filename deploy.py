import os
import shutil
from datetime import date
from random import randint
from acedistance.helpers.utilities.load_config import loadConfig


def deploy():
    configParser = loadConfig()

    # Set deployment meta data
    PACKAGE_NAME = 'acedistance'
    DEPLOY_VERSION = configParser['PROGRAM']['VERSION']
    DEPLOY_DATE = date.today().strftime("%d%m%Y")
    DEPLOY_SUFFIX = randint(1000, 9999)
    DEPLOY_DIR = f'{PACKAGE_NAME}_{DEPLOY_VERSION}_{DEPLOY_DATE}_{DEPLOY_SUFFIX}'

    # Create folder for deployment
    os.makedirs(DEPLOY_DIR)

    # Copy necessary packages, files and modules
    shutil.copytree(PACKAGE_NAME, os.path.join(DEPLOY_DIR, PACKAGE_NAME))
    shutil.copyfile('environment.yml', os.path.join(DEPLOY_DIR, 'environment.yml'))
    shutil.copyfile('estimate_distance.py', os.path.join(DEPLOY_DIR, 'estimate_distance.py'))
    shutil.copyfile('Makefile', os.path.join(DEPLOY_DIR, 'Makefile'))
    shutil.copyfile('README.md', os.path.join(DEPLOY_DIR, 'README.md'))
    shutil.copyfile('setup.sh', os.path.join(DEPLOY_DIR, 'setup.sh'))

    # Zip folder
    shutil.make_archive(f'{DEPLOY_DIR}_zip', 'zip', DEPLOY_DIR)


if __name__ == "__main__":
    deploy()
