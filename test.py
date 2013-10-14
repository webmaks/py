#!/usr/bin/env python
from email.MIMEMultipart import MIMEMultipart

msg = MIMEMultipart()
msg['From'] = 'test@test.ru'
msg['To'] = 'joe@mail.com'

print msg.as_string()

