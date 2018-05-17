c = get_config()

# Notebook config this is where you saved your pem cert
# c.NotebookApp.certfile = u'/home/ubuntu/certs/mycert.pem'
# Run on all IP addresses of your instance
c.NotebookApp.ip = '*'
# Don't open browser by default
c.NotebookApp.open_browser = False  
# Fix port to 8888
c.NotebookApp.port = 8888
# Disable token authentication
c.NotebookApp.token = ""
