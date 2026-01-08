class LoginPresenter:
    def __init__(self, view, api_client):
        self.view = view
        self.api = api_client
        # חיבור האירועים מה-View
        self.view.login_requested.connect(self.handle_login)

    def handle_login(self, email, password):
        # ה-Presenter מנהל את התקשורת (Restful API)
        response = self.api.login(email, password) # [cite: 35]
        if response.get("status") == "success":
            self.view.show_success("Welcome!")
        else:
            self.view.show_error("Failed to login")