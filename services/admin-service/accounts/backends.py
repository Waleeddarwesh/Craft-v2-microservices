from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class CaseInsensitiveModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        
        # In case the credential is passed in kwargs (e.g. email='...')
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
            
        if username:
            username = username.strip().lower()
            
            # Update kwargs if necessary
            if UserModel.USERNAME_FIELD in kwargs:
                kwargs[UserModel.USERNAME_FIELD] = username
                
        return super().authenticate(request, username=username, password=password, **kwargs)
