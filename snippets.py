#-------------------------------------------------------------------------------
# Qt Resource File
#-------------------------------------------------------------------------------
# Create the Qt resource file (.qrc) with Resource Editor
# Compile the .qrc file as a .py file :
# pyrcc4 -py3 F:\computing\Payrollv22\icon.qrc -o icon_rc.py

#-------------------------------------------------------------------------------
# Send mail
#-------------------------------------------------------------------------------
# coding: utf-8

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

msg = MIMEMultipart()
msg['From'] = 'XXX@gmail.com'
msg['To'] = 'YYY@gmail.com'
msg['Subject'] = 'Le sujet de mon mail' 
message = 'Bonjour !'
msg.attach(MIMEText(message))
mailserver = smtplib.SMTP('smtp.gmail.com', 587)
mailserver.ehlo()
mailserver.starttls()
mailserver.ehlo()
mailserver.login('XXX@gmail.com', 'APP_PASSWORD')
mailserver.sendmail('XXX@gmail.com', 'XXX@gmail.com', msg.as_string())
mailserver.quit()

# Generate Google app password : https://support.google.com/accounts/answer/185833?p=InvalidSecondFactor
