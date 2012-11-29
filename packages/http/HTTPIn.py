class HTTPIn():
    def __init__(self):
        self.method = "unknown"
        self.path = ""
        self.post_data = ""
        self.cookies = {}
        self.header_only = False
        self.auth_line = ""
        self.user_agent = ""
        self.session = None
