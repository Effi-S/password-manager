class Database:
    def __init__(self):
        self.session = Session()

    def add_password(self, site, username, password):
        new_entry = Password(site=site, username=username, password=password)
        self.session.add(new_entry)
        self.session.commit()

    def get_passwords(self):
        return self.session.query(Password).all()
