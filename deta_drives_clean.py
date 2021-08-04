from deta import Deta
from os import getenv

deta = Deta(getenv('DETA_PROJECT_KEY'))
drives = ['portraits', 'profiles']

for drive in drives:
    drive = deta.Drive(drive)
    try:
        drive.delete_many(drive.list()['names'])
    except AssertionError:
        pass