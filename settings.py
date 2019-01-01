#!/usr/bin/env python
# -*- coding: utf-8 -*-

import shelve
import const
import os

#-------------------------------------------------------------------------------
# These are the default values
#-------------------------------------------------------------------------------
defaultValues = [ 
    ['TIMER_PING', 500],
    ['TIMER_STATUS', 3000],
    ['UNREACHABLE_PING', 10],
    ['STATUS_GREEN', 50],
    ['STATUS_YELLOW', 200],
    ['SMTP_SERVER', "smtp.gmail.com"],
    ['SMTP_PORT', 587],
    ['SMTP_TLS', True],
    ['SMTP_USER', "sender@gmail.com"],
    ['SMTP_PASSWORD', "P@$$w0rd"],
    ['SMTP_RECIPIENTS', "user1@gmail.com; user2@gmail.com; user3@gmail.com"],
    ['ALT_PING_COMMAND', ""],
    ['ALT_PING_REGEX', ""],
    ['ALT_REGEX_GROUP', ""],
    ['ALT_PING_CODEPAGE', ""],
    ['ALT_PING_ENABLED', False]
]

#-------------------------------------------------------------------------------
# Open config file
#-------------------------------------------------------------------------------
db = shelve.open(os.path.join(os.path.join(os.path.expanduser("~"), const.APP_FOLDER), const.CONFIG_FILE))

#-------------------------------------------------------------------------------
 # Set default values if they not exists in config file
 #-------------------------------------------------------------------------------
for x in defaultValues:
   if not x[0] in db:
      db[x[0]] = x[1]

#-------------------------------------------------------------------------------
# Save config file
#-------------------------------------------------------------------------------
db.sync()

