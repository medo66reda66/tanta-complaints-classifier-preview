import hashlib
import hmac
import streamlit as st

_SALT = "80c3b64bbf3cb810"
_HASH = "658feafe1bcc309622286fe5e21d71efe428fc570d5ebe2f11a09a55b90659bf"


def require_admin():
    """Block the page until the admin password is entered."""
    if st.session_state.get("admin_ok"):
        return

    st.markdown("## 🔒 Admin access")
    st.write("This page is for administrators only. Enter the admin password to continue.")
    with st.form("admin_login"):
        pw = st.text_input("Admin password", type="password")
        go = st.form_submit_button("Sign in")
    if go:
        digest = hashlib.sha256((_SALT + pw).encode()).hexdigest()
        if hmac.compare_digest(digest, _HASH):
            st.session_state["admin_ok"] = True
            st.rerun()
        else:
            st.error("Wrong password.")
    st.stop()
