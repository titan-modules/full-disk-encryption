#!/usr/bin/env python
"""
This is a Titan module

- Analyze Users Enabled 
  for Full Disk Encryption

To use:

    sudo pip install --upgrade titantools

"""

import json
import logging
from sys import argv
from titantools.orm import TiORM
from titantools.data_science import DataScience
from titantools.system import execute_command as shell_out
from titantools import plist

# from sys import argv
from time import time, gmtime, strftime
from os.path import dirname,basename,isfile
from os import chmod
#from titantools.decorators import run_every_60

# Set Logging Status
logging_enabled = False

# Set datastore directory
DATASTORE = argv[1]

#@run_every_60
class AnalyzeFullDiskEncryption(object):
    """ AnalyzeFullDiskEncryption """

    def __init__(self):
      self.message = type(self).__name__
      self.status = 0
      self.datastore = []

    def get_full_disk_encryption(self):
      """
      Log FDE
      """
      # Create the temp plist file
      fde_users = [users for users in shell_out('sudo fdesetup list').split('\n') if not users in '']
      for user in fde_users:

        userdata = user.split(',')

        self.datastore.append({
          "date": exec_date,
          "name": userdata[0],
          "uuid": userdata[1]
          }) 

      # Set Message
      self.message = "Found %d FDE User" % len(self.datastore)

      # If no issues, return 0
      self.status = 0

    def analyze(self):
      """
      This is the 'main' method that launches all of the other checks
      """
      self.get_full_disk_encryption()

      return json.JSONEncoder().encode({"status": self.status, "message": self.message})

    def store(self):
      # the table definitions are stored in a library file. this is instantiating
      # the ORM object and initializing the tables
      module_schema_file = '%s/schema.json' % dirname(__file__)

      # Is file
      if isfile(module_schema_file):
        with open(module_schema_file) as schema_file:   
          schema = json.load(schema_file)

        # ORM 
        ORM = TiORM(DATASTORE)
        if isfile(DATASTORE):
            chmod(DATASTORE, 0600)
        for k, v in schema.iteritems():
            ORM.initialize_table(k, v)

        # Insert apps to database
        data_science = DataScience(ORM, self.datastore, "fde_users")
        data_science.get_new_entries()
        
if __name__ == "__main__":

    start = time()

    # the "exec_date" is used as the "date" field in the datastore
    exec_date = strftime("%a, %d %b %Y %H:%M:%S", gmtime())

    ###########################################################################
    # Gather data
    ###########################################################################
    try:
        a = AnalyzeFullDiskEncryption()
        if a is not None:
            output = a.analyze()
            a.store()
            print output

    except Exception, error:
        print error

    end = time()

    # to see how long this module took to execute, launch the module with
    # "--log" as a command line argument
    if "--log" in argv[1:]:
      logging_enabled = True
      logging.basicConfig(format='%(message)s', level=logging.INFO)
    
    logging.info("Execution took %s seconds.", str(end - start))
