"""Google OIDC via Streamlit's native authentication API."""
from dataclasses import dataclass
import streamlit as st

@dataclass(frozen=True)
class Identity:
    issuer:str; subject:str; email:str|None; name:str|None; picture:str|None

def require_google_login() -> Identity:
    if not getattr(st.user,'is_logged_in',False):
        st.title('🇵🇱 Polish Tutor')
        st.write('Sign in to load your placement test, study plan and lessons.')
        if st.button('Continue with Google',type='primary'):
            st.login()
        st.stop()
    subject=str(getattr(st.user,'sub','') or '')
    issuer=str(getattr(st.user,'iss','https://accounts.google.com') or 'https://accounts.google.com')
    if not subject:
        st.error('The identity provider did not return a stable subject identifier.')
        st.stop()
    return Identity(issuer,subject,getattr(st.user,'email',None),getattr(st.user,'name',None),getattr(st.user,'picture',None))
