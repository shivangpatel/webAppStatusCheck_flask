""" Interval to refresh status codes in seconds. """
refresh_interval = 4.0

""" File containing groups ofurls to check in json format. See included example 'checkurls.json'. """
filename = 'checkurls.json'

""" Message to display if sites are not connectable. """
site_down = 'UNREACHABLE'

""" Number of concurrent connections while checking sites. """
number_threads = 8

""" Enable a user submitted search through urls to verify they're in the file specified in 'filename'. """
include_search = True

""" Email Configuration """
MAIL_SERVER = 'smtp.anything.com'
MAIL_PORT = 465
MAIL_USERNAME = 'patelshivang@gmail.com'
MAIL_PASSWORD = 'xxxxx'
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_SUBJECT = 'MESSAGE FROM SITE MONITOR'
NOTIFICATION_RECIEVED_BY = ['patelshivang82@gmail.com', 'abc@xyz.com']