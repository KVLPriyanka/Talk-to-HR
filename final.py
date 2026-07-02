# import streamlit as st
# import qrcode
# from io import BytesIO
# import streamlit as st
# import sqlite3
# import hashlib
# from datetime import datetime
# import io
# import socket
# import qrcode
# from urllib.parse import urlencode
# from PIL import Image
# # Page configuration
# st.set_page_config(page_title="Standalone QR Code Generator", page_icon="🖨️", layout="centered")

# st.title("🖨️ Standalone QR Code Generator")
# st.write("Enter your HR portal URL or any link below to generate an instant, downloadable QR code.")

# # Text input for the URL
# target_url = st.text_input(
#     "Paste your Portal Link / URL here:", 
#     placeholder="https://share.streamlit.io/your-username/your-hr-app"
# )

# if target_url:
#     try:
#         # Configuration for the QR code
#         qr = qrcode.QRCode(
#             version=1,
#             error_correction=qrcode.constants.ERROR_CORRECT_L,
#             box_size=10,
#             border=4,
#         )
#         qr.add_data(target_url)
#         qr.make(fit=True)

#         # Create the image
#         img = qr.make_image(fill_color="black", back_color="white")
        
#         # Save image to a bytes buffer so Streamlit can read/download it
#         buf = BytesIO()
#         img.save(buf, format="PNG")
#         byte_im = buf.getvalue()

#         st.markdown("---")
#         st.subheader("Your Generated QR Code:")
        
#         # Display the QR code image on the main screen
#         st.image(byte_im, width=300, caption="Scan this with a mobile camera")

#         # Provide a quick download option
#         st.download_button(
#             label="💾 Download QR Code (PNG)",
#             data=byte_im,
#             file_name="hr_portal_qrcode.png",
#             mime="image/png",
#             type="primary"
#         )
        
#     except Exception as e:
#         st.error(f"Something went wrong: {e}")
# else:
#     st.info("💡 Waiting for a valid URL link to generate the QR code...")
# ================================================================================================



import streamlit as st
import sqlite3
import hashlib
import secrets
import base64
from datetime import datetime, timedelta
import pandas as pd

st.set_page_config(page_title="Talk To HR ...", page_icon="📋", layout="wide")

DB_FILE = "portal.db"
BACKGROUND_IMAGE = "123.jpg"
LOGO_IMAGE = "meil_logo.png"


def get_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def add_background(image_path):
    encoded = get_base64(image_path)
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpeg;base64,{encoded}");
            background-size: cover;
            background-position: center center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        .stApp::before {{
            content: "";
            position: fixed;
            inset: 0;
            background: rgba(0, 0, 0, 0.45);
            z-index: 0;
        }}
        .block-container, header, footer {{
            position: relative;
            z-index: 1;
        }}
        [data-testid="stHeader"] {{
            background: transparent;
        }}
        [data-testid="stSidebar"] {{
            background: rgba(15, 23, 42, 0.92);
        }}
        /* Limit form/control widths to roughly half the page and shrink the wrapper
           so there is no extra dark block to the right of inputs */
        div[data-testid="stTextInput"],
        div[data-testid="stTextArea"],
        div[data-testid="stSelectbox"],
        div[data-testid="stMultiSelect"] {{
            width: 50% !important;
            max-width: 720px !important;
            box-sizing: border-box;
            background: transparent !important;
            padding: 0 !important;
            margin-bottom: 1rem !important;
            display: inline-block !important;
        }}
        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea,
        div[data-testid="stSelectbox"] div[role="combobox"],
        div[data-testid="stMultiSelect"] div[role="listbox"] {{
            width: 100% !important;
            background: rgba(29, 31, 45, 0.95) !important;
            color: white !important;
            border-radius: 10px !important;
            box-sizing: border-box;
        }}
        /* Make sure form buttons align nicely with the shorter inputs */
        .stButton > button {{
            margin-top: 0.6rem;
        }}
        .top-right-logo {{
            position: fixed;
            top: 18px;
            right: 22px;
            z-index: 9999;
            width: 110px;
        }}
        .top-right-logo img {{
            width: 100%;
            height: auto;
            display: block;
        }}
        </style>
        <div class="top-right-logo">
            <img src="data:image/jpg;base64,{get_base64(LOGO_IMAGE)}" />
        </div>
        """,
        unsafe_allow_html=True,
    )


add_background(BACKGROUND_IMAGE)


def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            role TEXT,
            full_name TEXT,
            mobile_number TEXT,
            employee_id TEXT,
            is_active INTEGER DEFAULT 1
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            type TEXT,
            subject TEXT,
            description TEXT,
            status TEXT,
            hr_notes TEXT,
            timestamp TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            username TEXT PRIMARY KEY,
            token TEXT,
            expires_at TEXT
        )
    """)

    c.execute("PRAGMA table_info(users)")
    cols = [row[1] for row in c.fetchall()]
    if "mobile_number" not in cols:
        c.execute("ALTER TABLE users ADD COLUMN mobile_number TEXT")
    if "employee_id" not in cols:
        c.execute("ALTER TABLE users ADD COLUMN employee_id TEXT")
    if "is_active" not in cols:
        c.execute("ALTER TABLE users ADD COLUMN is_active INTEGER DEFAULT 1")
        c.execute("UPDATE users SET is_active = 1 WHERE is_active IS NULL")

    c.execute("SELECT * FROM users WHERE username='hr@portal.com'")
    if not c.fetchone():
        hashed_pw = hashlib.sha256("hrpass123".encode()).hexdigest()
        c.execute(
            """
            INSERT INTO users
            (username, password, role, full_name, mobile_number, employee_id, is_active)
            VALUES (?, ?, 'HR', ?, ?, ?, 1)
            """,
            ("hr@portal.com", hashed_pw, "HR Administrator", "9999999999", "HR001"),
        )

    conn.commit()
    conn.close()


init_db()


def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()


def check_login(username, password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        """
        SELECT role, full_name, is_active
        FROM users
        WHERE username=? AND password=?
        """,
        (username, make_hashes(password)),
    )
    row = c.fetchone()
    conn.close()
    return row


def register_user(username, password, full_name, mobile_number, employee_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute(
            """
            INSERT INTO users
            (username, password, role, full_name, mobile_number, employee_id, is_active)
            VALUES (?, ?, 'Applicant', ?, ?, ?, 1)
            """,
            (username, make_hashes(password), full_name, mobile_number, employee_id),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def reset_password(username, employee_id, mobile_number, new_password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        """
        SELECT username
        FROM users
        WHERE username=? AND employee_id=? AND mobile_number=? AND is_active=1
        """,
        (username, employee_id, mobile_number),
    )
    row = c.fetchone()
    if not row:
        conn.close()
        return False

    c.execute("UPDATE users SET password=? WHERE username=?", (make_hashes(new_password), username))
    conn.commit()
    conn.close()
    return True


def create_ticket(username, form_type, subject, description):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute(
        """
        INSERT INTO tickets
        (username, type, subject, description, status, hr_notes, timestamp)
        VALUES (?, ?, ?, ?, 'Pending Review', 'No response yet', ?)
        """,
        (username, form_type, subject, description, ts),
    )
    conn.commit()
    conn.close()


def get_all_tickets_df():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query(
        """
        SELECT id AS "Ticket ID",
               username AS "Applicant",
               type AS "Type",
               subject AS "Subject",
               status AS "Current Status",
               timestamp AS "Date Filed"
        FROM tickets
        ORDER BY id DESC
        """,
        conn,
    )
    conn.close()
    return df


def get_ticket_by_id(ticket_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        """
        SELECT id, username, type, subject, description, status, hr_notes, timestamp
        FROM tickets
        WHERE id=?
        """,
        (ticket_id,),
    )
    row = c.fetchone()
    conn.close()
    return row


def update_ticket(ticket_id, status, notes):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE tickets SET status=?, hr_notes=? WHERE id=?", (status, notes, ticket_id))
    conn.commit()
    conn.close()


def get_users_df():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query(
        """
        SELECT username AS "Username",
               full_name AS "Full Name",
               employee_id AS "Employee ID",
               mobile_number AS "Mobile Number",
               role AS "Role",
               CASE WHEN is_active = 1 THEN 1 ELSE 0 END AS "Active"
        FROM users
        ORDER BY username
        """,
        conn,
    )
    conn.close()
    df["Active"] = df["Active"].astype(bool)
    return df


def set_user_active(username, active):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET is_active=? WHERE username=?", (1 if active else 0, username))
    conn.commit()
    conn.close()


def is_user_active(username):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT is_active FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    return bool(row[0]) if row else False


def create_session(username):
    token = secrets.token_urlsafe(32)
    expires_at = (datetime.utcnow() + timedelta(days=7)).isoformat()

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM sessions WHERE username=?", (username,))
    c.execute("INSERT INTO sessions (username, token, expires_at) VALUES (?, ?, ?)", (username, token, expires_at))
    conn.commit()
    conn.close()
    return token


def clear_session(username):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM sessions WHERE username=?", (username,))
    conn.commit()
    conn.close()


def restore_login():
    try:
        token = st.query_params.get("auth", None)
        if isinstance(token, list):
            token = token[0]
        if not token:
            return

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(
            """
            SELECT u.username, u.role, u.full_name, u.is_active, s.expires_at
            FROM sessions s
            JOIN users u ON u.username = s.username
            WHERE s.token=?
            """,
            (token,),
        )
        row = c.fetchone()
        conn.close()

        if not row:
            return

        username, role, full_name, active_flag, expires_at = row
        if not active_flag:
            return
        if datetime.utcnow() > datetime.fromisoformat(expires_at):
            return

        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.role = role
        st.session_state.full_name = full_name
    except Exception:
        return


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.full_name = ""
    st.session_state.selected_ticket_id = None

restore_login()


def logout():
    clear_session(st.session_state.username)
    st.query_params.clear()
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.full_name = ""
    st.session_state.selected_ticket_id = None
    st.rerun()


if not st.session_state.logged_in:
    st.title("👩‍💻 Talk To HR '🤝...")
    st.write("Welcome! Please sign up or log in below to access the submission forms.")

    login_tab, signup_tab, forgot_tab = st.tabs(["🔑 Log In", "📝 Sign Up (New Applicants)", "❓ Forgot Password"])

    with login_tab:
        st.subheader("Login to Your Account")
        col1, col2 = st.columns([1, 1])
        with col1:
            login_user = st.text_input("Email / Username", key="l_user").strip().lower()
            login_pass = st.text_input("Password", type="password", key="l_pass")

            if st.button("Log In", type="primary"):
                user_info = check_login(login_user, login_pass)
                if user_info:
                    role, full_name, active_flag = user_info
                    if not active_flag:
                        st.error("❌ Your account is inactive. Contact HR.")
                    else:
                        st.session_state.logged_in = True
                        st.session_state.username = login_user
                        st.session_state.role = role
                        st.session_state.full_name = full_name
                        token = create_session(login_user)
                        st.query_params["auth"] = token
                        st.rerun()
                else:
                    st.error("❌ Incorrect username or password. (HR: hr@portal.com / hrpass123)")

    with signup_tab:
        st.subheader("Create an Applicant Profile")
        col1, col2 = st.columns([1, 1])
        with col1:
            new_name = st.text_input("Full Name")
            new_user = st.text_input("Email Address (Username)", key="s_user").strip().lower()
        with col2:
            new_mobile = st.text_input("Mobile Number")
            new_empid = st.text_input("Employee ID")

        new_pass = st.text_input("Create Password", type="password", key="s_pass")

        if st.button("Register & Create Account"):
            if not new_name or not new_user or not new_mobile or not new_empid or not new_pass:
                st.error("❌ Please fill out all fields.")
            elif not new_mobile.isdigit() or len(new_mobile) != 10:
                st.error("❌ Mobile number must be exactly 10 digits.")
            else:
                if register_user(new_user, new_pass, new_name, new_mobile, new_empid):
                    st.success("🎉 Account created successfully! Now log in from the Login tab.")
                else:
                    st.error("❌ An account with this email already exists.")

    with forgot_tab:
        st.subheader("Reset Your Password")
        col1, col2 = st.columns([1, 1])
        with col1:
            fp_user = st.text_input("Username / Email", key="fp_user").strip().lower()
            fp_empid = st.text_input("Employee ID", key="fp_empid")
        with col2:
            fp_mobile = st.text_input("Mobile Number", key="fp_mobile")
            fp_new = st.text_input("New Password", type="password", key="fp_new")

        fp_confirm = st.text_input("Confirm New Password", type="password", key="fp_confirm")

        if st.button("Reset Password"):
            if not fp_user or not fp_empid or not fp_mobile or not fp_new or not fp_confirm:
                st.error("❌ Please fill out all fields.")
            elif fp_new != fp_confirm:
                st.error("❌ New password and confirm password do not match.")
            else:
                if reset_password(fp_user, fp_empid, fp_mobile, fp_new):
                    st.success("✅ Password reset successfully. You can now log in.")
                else:
                    st.error("❌ Invalid details or inactive account.")

else:
    st.sidebar.title(f"👤 {st.session_state.full_name}")
    st.sidebar.write(f"**Logged in as:** {st.session_state.role}")
    if st.sidebar.button("Logout", type="secondary"):
        logout()

    if not is_user_active(st.session_state.username):
        st.error("❌ Your account has been set to inactive. Access is blocked.")
        st.stop()

    if st.session_state.role == "Applicant":
        st.title("📋 Applicant Dashboard")
        app_tabs = st.tabs(["📝 Open New Request", "🔍 View My Portal History"])

        with app_tabs[0]:
            st.subheader("Submit New Feedback or Complaint")
            with st.form("submission_form", clear_on_submit=True):
                form_type = st.selectbox("Form Category", ["Feedback", "Complaint", "Suggestion"])
                subject = st.text_input("Subject Heading")
                description = st.text_area("Detailed Information")
                submit_btn = st.form_submit_button("Submit Form to HR")

            if submit_btn:
                if not subject or not description:
                    st.error("❌ Please complete both the Subject and Description fields.")
                else:
                    create_ticket(st.session_state.username, form_type, subject, description)
                    st.success("🎉 Form submitted successfully!")

        with app_tabs[1]:
            st.subheader("Your Submission History & Status")
            conn = sqlite3.connect(DB_FILE)
            user_df = pd.read_sql_query(
                """
                SELECT id AS "Ticket ID",
                       timestamp AS "Submitted On",
                       type AS "Type",
                       subject AS "Subject",
                       description AS "Your Message",
                       status AS "Status",
                       hr_notes AS "HR Response / Action Notes"
                FROM tickets
                WHERE username=?
                ORDER BY id DESC
                """,
                conn,
                params=(st.session_state.username,),
            )
            conn.close()

            if user_df.empty:
                st.info("You haven't submitted any tickets yet.")
            else:
                st.dataframe(user_df, use_container_width=True, hide_index=True)

    elif st.session_state.role == "HR":
        st.title("🛠️ HR Management Control Panel")

        user_tab, ticket_tab = st.tabs(["👥 User Active/Inactive", "📋 Ticket Master List"])

        with user_tab:
            st.subheader("Manage User Access")
            users_df = get_users_df()

            edited_users = st.data_editor(
                users_df,
                use_container_width=True,
                hide_index=True,
                column_config={"Active": st.column_config.CheckboxColumn("Active")},
                disabled=["Username", "Full Name", "Employee ID", "Mobile Number", "Role"],
                key="users_editor",
            )

            if st.button("Save User Access Changes"):
                for _, row in edited_users.iterrows():
                    set_user_active(row["Username"], bool(row["Active"]))
                st.success("✅ User access updated.")
                st.rerun()

        with ticket_tab:
            st.subheader("Master List of Applicant Submissions")

            all_tickets_df = get_all_tickets_df()

            if all_tickets_df.empty:
                st.info("No forms have been submitted by applicants yet.")
            else:
                event = st.dataframe(
                    all_tickets_df,
                    use_container_width=True,
                    hide_index=True,
                    on_select="rerun",
                    selection_mode="single-row",
                )

                selected_rows = event.selection.rows if event and event.selection else []
                if selected_rows:
                    selected_row = all_tickets_df.iloc[selected_rows[0]]
                    st.session_state.selected_ticket_id = int(selected_row["Ticket ID"])
                elif st.session_state.selected_ticket_id is None:
                    st.session_state.selected_ticket_id = int(all_tickets_df.iloc[0]["Ticket ID"])

                st.markdown("---")
                st.subheader("Review & Action Center")

                current_ticket = get_ticket_by_id(st.session_state.selected_ticket_id)

                if current_ticket:
                    st.info(f"Reviewing Ticket #{current_ticket[0]} submitted by {current_ticket[1]}")
                    st.write(f"**Category:** {current_ticket[2]} | **Subject:** {current_ticket[3]}")
                    st.text_area("Applicant's Original Message", value=current_ticket[4], disabled=True)

                    with st.form("hr_processing_form"):
                        updated_status = st.selectbox(
                            "Update Status",
                            ["Pending Review", "Action Taken", "Resolved"],
                            index=["Pending Review", "Action Taken", "Resolved"].index(current_ticket[5])
                            if current_ticket[5] in ["Pending Review", "Action Taken", "Resolved"]
                            else 0,
                        )
                        updated_notes = st.text_area("Add HR Response / Resolution Notes", value=current_ticket[6])
                        save_btn = st.form_submit_button("Submit")

                    if save_btn:
                        update_ticket(st.session_state.selected_ticket_id, updated_status, updated_notes)
                        st.success(f"✅ Ticket #{st.session_state.selected_ticket_id} updated.")
                        st.rerun()


# ===================================

# import streamlit as st
# import sqlite3
# import hashlib
# import secrets
# import base64
# from datetime import datetime, timedelta
# import pandas as pd

# st.set_page_config(page_title="Talk To HR ...", page_icon="📋", layout="wide")

# DB_FILE = "portal.db"
# BACKGROUND_IMAGE = "123.jpg"
# LOGO_IMAGE = "meil_logo.png"


# def get_base64(file_path):
#     with open(file_path, "rb") as f:
#         return base64.b64encode(f.read()).decode()


# def add_background(image_path):
#     encoded_bg = get_base64(image_path)
#     encoded_logo = get_base64(LOGO_IMAGE)

#     st.markdown(
#         f"""
#         <style>
#         .stApp {{
#             background-image: url("data:image/jpeg;base64,{encoded_bg}");
#             background-size: cover;
#             background-position: center center;
#             background-repeat: no-repeat;
#             background-attachment: fixed;
#         }}

#         .stApp::before {{
#             content: "";
#             position: fixed;
#             inset: 0;
#             background: rgba(0, 0, 0, 0.42);
#             z-index: 0;
#         }}

#         .block-container, header, footer {{
#             position: relative;
#             z-index: 1;
#         }}

#         [data-testid="stHeader"] {{
#             background: transparent;
#         }}

#         [data-testid="stSidebar"] {{
#             background: rgba(15, 23, 42, 0.92);
#         }}

#         .top-right-logo {{
#             position: fixed;
#             top: 18px;
#             right: 22px;
#             z-index: 9999;
#             width: 140px;
#             background: rgba(255,255,255,0.95);
#             padding: 14px;
#             border-radius: 2px;
#             box-shadow: 0 8px 24px rgba(0,0,0,0.18);
#         }}

#         .top-right-logo img {{
#             width: 100%;
#             height: auto;
#             display: block;
#         }}

#         .main-title {{
#             color: white;
#             font-size: 4rem;
#             font-weight: 800;
#             line-height: 1.05;
#             margin-top: 4rem;
#             margin-bottom: 0.5rem;
#             text-shadow: 0 2px 10px rgba(0,0,0,0.25);
#         }}

#         .main-subtitle {{
#             color: rgba(255,255,255,0.92);
#             font-size: 1.15rem;
#             margin-bottom: 1.5rem;
#         }}

#         .stTabs [data-baseweb="tab-list"] {{
#             gap: 18px;
#             border-bottom: 1px solid rgba(255,255,255,0.15);
#         }}

#         .stTabs [data-baseweb="tab"] {{
#             color: rgba(255,255,255,0.9);
#             font-weight: 500;
#             padding: 0.25rem 0rem 0.9rem 0rem;
#         }}

#         .stTabs [aria-selected="true"] {{
#             color: #ff5b57 !important;
#         }}

#         .stTabs [aria-selected="true"]::after {{
#             content: "";
#             display: block;
#             height: 3px;
#             margin-top: 10px;
#             background: #ff5b57;
#             border-radius: 999px;
#         }}

#         div[data-testid="stTextInput"] label,
#         div[data-testid="stTextArea"] label,
#         div[data-testid="stSelectbox"] label {{
#             color: white !important;
#             font-size: 1rem;
#         }}

#         div[data-testid="stTextInput"] input,
#         div[data-testid="stTextArea"] textarea,
#         div[data-testid="stSelectbox"] div[role="combobox"] {{
#             background: rgba(29, 31, 45, 0.95) !important;
#             color: white !important;
#             border: 1px solid rgba(255,255,255,0.18) !important;
#             border-radius: 10px !important;
#         }}

#         div[data-testid="stTextInput"] input:focus,
#         div[data-testid="stTextArea"] textarea:focus {{
#             border: 1px solid #ff5b57 !important;
#             box-shadow: 0 0 0 1px #ff5b57 !important;
#         }}

#         .stButton > button {{
#             background: #ff5b57;
#             color: white;
#             border: none;
#             border-radius: 12px;
#             padding: 0.7rem 1.5rem;
#             font-weight: 600;
#         }}

#         .stButton > button:hover {{
#             background: #ff4340;
#             color: white;
#         }}

#         .stAlert {{
#             background: rgba(255,255,255,0.08);
#         }}
#         </style>

#         <div class="top-right-logo">
#             <img src="data:image/png;base64,{encoded_logo}" />
#         </div>
#         """,
#         unsafe_allow_html=True,
#     )


# add_background(BACKGROUND_IMAGE)


# def init_db():
#     conn = sqlite3.connect(DB_FILE)
#     c = conn.cursor()

#     c.execute("""
#         CREATE TABLE IF NOT EXISTS users (
#             username TEXT PRIMARY KEY,
#             password TEXT,
#             role TEXT,
#             full_name TEXT,
#             mobile_number TEXT,
#             employee_id TEXT,
#             is_active INTEGER DEFAULT 1
#         )
#     """)

#     c.execute("""
#         CREATE TABLE IF NOT EXISTS tickets (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             username TEXT,
#             type TEXT,
#             subject TEXT,
#             description TEXT,
#             status TEXT,
#             hr_notes TEXT,
#             timestamp TEXT
#         )
#     """)

#     c.execute("""
#         CREATE TABLE IF NOT EXISTS sessions (
#             username TEXT PRIMARY KEY,
#             token TEXT,
#             expires_at TEXT
#         )
#     """)

#     c.execute("PRAGMA table_info(users)")
#     cols = [row[1] for row in c.fetchall()]
#     if "mobile_number" not in cols:
#         c.execute("ALTER TABLE users ADD COLUMN mobile_number TEXT")
#     if "employee_id" not in cols:
#         c.execute("ALTER TABLE users ADD COLUMN employee_id TEXT")
#     if "is_active" not in cols:
#         c.execute("ALTER TABLE users ADD COLUMN is_active INTEGER DEFAULT 1")
#         c.execute("UPDATE users SET is_active = 1 WHERE is_active IS NULL")

#     c.execute("SELECT * FROM users WHERE username='hr@portal.com'")
#     if not c.fetchone():
#         hashed_pw = hashlib.sha256("hrpass123".encode()).hexdigest()
#         c.execute(
#             """
#             INSERT INTO users
#             (username, password, role, full_name, mobile_number, employee_id, is_active)
#             VALUES (?, ?, 'HR', ?, ?, ?, 1)
#             """,
#             ("hr@portal.com", hashed_pw, "HR Administrator", "9999999999", "HR001"),
#         )

#     conn.commit()
#     conn.close()


# init_db()


# def make_hashes(password):
#     return hashlib.sha256(str.encode(password)).hexdigest()


# def check_login(username, password):
#     conn = sqlite3.connect(DB_FILE)
#     c = conn.cursor()
#     c.execute(
#         """
#         SELECT role, full_name, is_active
#         FROM users
#         WHERE username=? AND password=?
#         """,
#         (username, make_hashes(password)),
#     )
#     row = c.fetchone()
#     conn.close()
#     return row


# def register_user(username, password, full_name, mobile_number, employee_id):
#     conn = sqlite3.connect(DB_FILE)
#     c = conn.cursor()
#     try:
#         c.execute(
#             """
#             INSERT INTO users
#             (username, password, role, full_name, mobile_number, employee_id, is_active)
#             VALUES (?, ?, 'Applicant', ?, ?, ?, 1)
#             """,
#             (username, make_hashes(password), full_name, mobile_number, employee_id),
#         )
#         conn.commit()
#         return True
#     except sqlite3.IntegrityError:
#         return False
#     finally:
#         conn.close()


# def reset_password(username, employee_id, mobile_number, new_password):
#     conn = sqlite3.connect(DB_FILE)
#     c = conn.cursor()
#     c.execute(
#         """
#         SELECT username
#         FROM users
#         WHERE username=? AND employee_id=? AND mobile_number=? AND is_active=1
#         """,
#         (username, employee_id, mobile_number),
#     )
#     row = c.fetchone()
#     if not row:
#         conn.close()
#         return False

#     c.execute("UPDATE users SET password=? WHERE username=?", (make_hashes(new_password), username))
#     conn.commit()
#     conn.close()
#     return True


# def create_ticket(username, form_type, subject, description):
#     conn = sqlite3.connect(DB_FILE)
#     c = conn.cursor()
#     ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     c.execute(
#         """
#         INSERT INTO tickets
#         (username, type, subject, description, status, hr_notes, timestamp)
#         VALUES (?, ?, ?, ?, 'Pending Review', 'No response yet', ?)
#         """,
#         (username, form_type, subject, description, ts),
#     )
#     conn.commit()
#     conn.close()


# def get_all_tickets_df():
#     conn = sqlite3.connect(DB_FILE)
#     df = pd.read_sql_query(
#         """
#         SELECT id AS "Ticket ID",
#                username AS "Applicant",
#                type AS "Type",
#                subject AS "Subject",
#                status AS "Current Status",
#                timestamp AS "Date Filed"
#         FROM tickets
#         ORDER BY id DESC
#         """,
#         conn,
#     )
#     conn.close()
#     return df


# def get_ticket_by_id(ticket_id):
#     conn = sqlite3.connect(DB_FILE)
#     c = conn.cursor()
#     c.execute(
#         """
#         SELECT id, username, type, subject, description, status, hr_notes, timestamp
#         FROM tickets
#         WHERE id=?
#         """,
#         (ticket_id,),
#     )
#     row = c.fetchone()
#     conn.close()
#     return row


# def update_ticket(ticket_id, status, notes):
#     conn = sqlite3.connect(DB_FILE)
#     c = conn.cursor()
#     c.execute("UPDATE tickets SET status=?, hr_notes=? WHERE id=?", (status, notes, ticket_id))
#     conn.commit()
#     conn.close()


# def get_users_df():
#     conn = sqlite3.connect(DB_FILE)
#     df = pd.read_sql_query(
#         """
#         SELECT username AS "Username",
#                full_name AS "Full Name",
#                employee_id AS "Employee ID",
#                mobile_number AS "Mobile Number",
#                role AS "Role",
#                CASE WHEN is_active = 1 THEN 1 ELSE 0 END AS "Active"
#         FROM users
#         ORDER BY username
#         """,
#         conn,
#     )
#     conn.close()
#     df["Active"] = df["Active"].astype(bool)
#     return df


# def set_user_active(username, active):
#     conn = sqlite3.connect(DB_FILE)
#     c = conn.cursor()
#     c.execute("UPDATE users SET is_active=? WHERE username=?", (1 if active else 0, username))
#     conn.commit()
#     conn.close()


# def is_user_active(username):
#     conn = sqlite3.connect(DB_FILE)
#     c = conn.cursor()
#     c.execute("SELECT is_active FROM users WHERE username=?", (username,))
#     row = c.fetchone()
#     conn.close()
#     return bool(row[0]) if row else False


# def create_session(username):
#     token = secrets.token_urlsafe(32)
#     expires_at = (datetime.utcnow() + timedelta(days=7)).isoformat()

#     conn = sqlite3.connect(DB_FILE)
#     c = conn.cursor()
#     c.execute("DELETE FROM sessions WHERE username=?", (username,))
#     c.execute("INSERT INTO sessions (username, token, expires_at) VALUES (?, ?, ?)", (username, token, expires_at))
#     conn.commit()
#     conn.close()
#     return token


# def clear_session(username):
#     conn = sqlite3.connect(DB_FILE)
#     c = conn.cursor()
#     c.execute("DELETE FROM sessions WHERE username=?", (username,))
#     conn.commit()
#     conn.close()


# def restore_login():
#     try:
#         token = st.query_params.get("auth", None)
#         if isinstance(token, list):
#             token = token[0]
#         if not token:
#             return

#         conn = sqlite3.connect(DB_FILE)
#         c = conn.cursor()
#         c.execute(
#             """
#             SELECT u.username, u.role, u.full_name, u.is_active, s.expires_at
#             FROM sessions s
#             JOIN users u ON u.username = s.username
#             WHERE s.token=?
#             """,
#             (token,),
#         )
#         row = c.fetchone()
#         conn.close()

#         if not row:
#             return

#         username, role, full_name, active_flag, expires_at = row
#         if not active_flag:
#             return
#         if datetime.utcnow() > datetime.fromisoformat(expires_at):
#             return

#         st.session_state.logged_in = True
#         st.session_state.username = username
#         st.session_state.role = role
#         st.session_state.full_name = full_name
#     except Exception:
#         return


# if "logged_in" not in st.session_state:
#     st.session_state.logged_in = False
#     st.session_state.username = ""
#     st.session_state.role = ""
#     st.session_state.full_name = ""
#     st.session_state.selected_ticket_id = None


# restore_login()


# def logout():
#     clear_session(st.session_state.username)
#     st.query_params.clear()
#     st.session_state.logged_in = False
#     st.session_state.username = ""
#     st.session_state.role = ""
#     st.session_state.full_name = ""
#     st.session_state.selected_ticket_id = None
#     st.rerun()


# if not st.session_state.logged_in:
#     st.markdown('<div class="main-title">👩‍💻 Talk To HR &#39; 🤝 ...</div>', unsafe_allow_html=True)
#     st.markdown(
#         '<div class="main-subtitle">Welcome! Please sign up or log in below to access the submission forms.</div>',
#         unsafe_allow_html=True,
#     )

#     login_tab, signup_tab, forgot_tab = st.tabs(["🔑 Log In", "📝 Sign Up (New Applicants)", "❓ Forgot Password"])

#     with login_tab:
#         st.subheader("Login to Your Account")
#         col1, col2, col3 = st.columns([2, 3, 2])
#         with col2:
#             login_user = st.text_input("Email / Username", key="l_user").strip().lower()
#             login_pass = st.text_input("Password", type="password", key="l_pass")

#             if st.button("Log In", type="primary"):
#                 user_info = check_login(login_user, login_pass)
#                 if user_info:
#                     role, full_name, active_flag = user_info
#                     if not active_flag:
#                         st.error("❌ Your account is inactive. Contact HR.")
#                     else:
#                         st.session_state.logged_in = True
#                         st.session_state.username = login_user
#                         st.session_state.role = role
#                         st.session_state.full_name = full_name
#                         token = create_session(login_user)
#                         st.query_params["auth"] = token
#                         st.rerun()
#                 else:
#                     st.error("❌ Incorrect username or password. (HR: hr@portal.com / hrpass123)")

#     with signup_tab:
#         st.subheader("Create an Applicant Profile")
#         col1, col2, col3 = st.columns([2, 3, 2])
#         with col2:
#             new_name = st.text_input("Full Name")
#             new_user = st.text_input("Email Address (Username)", key="s_user").strip().lower()
#             new_mobile = st.text_input("Mobile Number")
#             new_empid = st.text_input("Employee ID")
#             new_pass = st.text_input("Create Password", type="password", key="s_pass")

#             if st.button("Register & Create Account"):
#                 if not new_name or not new_user or not new_mobile or not new_empid or not new_pass:
#                     st.error("❌ Please fill out all fields.")
#                 elif not new_mobile.isdigit() or len(new_mobile) != 10:
#                     st.error("❌ Mobile number must be exactly 10 digits.")
#                 else:
#                     if register_user(new_user, new_pass, new_name, new_mobile, new_empid):
#                         st.success("🎉 Account created successfully! Now log in from the Login tab.")
#                     else:
#                         st.error("❌ An account with this email already exists.")

#     with forgot_tab:
#         st.subheader("Reset Your Password")
#         col1, col2, col3 = st.columns([2, 3, 2])
#         with col2:
#             fp_user = st.text_input("Username / Email", key="fp_user").strip().lower()
#             fp_empid = st.text_input("Employee ID", key="fp_empid")
#             fp_mobile = st.text_input("Mobile Number", key="fp_mobile")
#             fp_new = st.text_input("New Password", type="password", key="fp_new")
#             fp_confirm = st.text_input("Confirm New Password", type="password", key="fp_confirm")

#             if st.button("Reset Password"):
#                 if not fp_user or not fp_empid or not fp_mobile or not fp_new or not fp_confirm:
#                     st.error("❌ Please fill out all fields.")
#                 elif fp_new != fp_confirm:
#                     st.error("❌ New password and confirm password do not match.")
#                 else:
#                     if reset_password(fp_user, fp_empid, fp_mobile, fp_new):
#                         st.success("✅ Password reset successfully. You can now log in.")
#                     else:
#                         st.error("❌ Invalid details or inactive account.")

# else:
#     st.sidebar.title(f"👤 {st.session_state.full_name}")
#     st.sidebar.write(f"**Logged in as:** {st.session_state.role}")
#     if st.sidebar.button("Logout", type="secondary"):
#         logout()

#     if not is_user_active(st.session_state.username):
#         st.error("❌ Your account has been set to inactive. Access is blocked.")
#         st.stop()

#     if st.session_state.role == "Applicant":
#         st.title("📋 Applicant Dashboard")
#         app_tabs = st.tabs(["📝 Open New Request", "🔍 View My Portal History"])

#         with app_tabs[0]:
#             st.subheader("Submit New Feedback or Complaint")
#             with st.form("submission_form", clear_on_submit=True):
#                 form_type = st.selectbox("Form Category", ["Feedback", "Complaint", "Suggestion"])
#                 subject = st.text_input("Subject Heading")
#                 description = st.text_area("Detailed Information")
#                 submit_btn = st.form_submit_button("Submit Form to HR")

#             if submit_btn:
#                 if not subject or not description:
#                     st.error("❌ Please complete both the Subject and Description fields.")
#                 else:
#                     create_ticket(st.session_state.username, form_type, subject, description)
#                     st.success("🎉 Form submitted successfully!")

#         with app_tabs[1]:
#             st.subheader("Your Submission History & Status")
#             conn = sqlite3.connect(DB_FILE)
#             user_df = pd.read_sql_query(
#                 """
#                 SELECT id AS "Ticket ID",
#                        timestamp AS "Submitted On",
#                        type AS "Type",
#                        subject AS "Subject",
#                        description AS "Your Message",
#                        status AS "Status",
#                        hr_notes AS "HR Response / Action Notes"
#                 FROM tickets
#                 WHERE username=?
#                 ORDER BY id DESC
#                 """,
#                 conn,
#                 params=(st.session_state.username,),
#             )
#             conn.close()

#             if user_df.empty:
#                 st.info("You haven't submitted any tickets yet.")
#             else:
#                 st.dataframe(user_df, use_container_width=True, hide_index=True)

#     elif st.session_state.role == "HR":
#         st.title("🛠️ HR Management Control Panel")

#         user_tab, ticket_tab = st.tabs(["👥 User Active/Inactive", "📋 Ticket Master List"])

#         with user_tab:
#             st.subheader("Manage User Access")
#             users_df = get_users_df()

#             edited_users = st.data_editor(
#                 users_df,
#                 use_container_width=True,
#                 hide_index=True,
#                 column_config={"Active": st.column_config.CheckboxColumn("Active")},
#                 disabled=["Username", "Full Name", "Employee ID", "Mobile Number", "Role"],
#                 key="users_editor",
#             )

#             if st.button("Save User Access Changes"):
#                 for _, row in edited_users.iterrows():
#                     set_user_active(row["Username"], bool(row["Active"]))
#                 st.success("✅ User access updated.")
#                 st.rerun()

#         with ticket_tab:
#             st.subheader("Master List of Applicant Submissions")

#             all_tickets_df = get_all_tickets_df()

#             if all_tickets_df.empty:
#                 st.info("No forms have been submitted by applicants yet.")
#             else:
#                 event = st.dataframe(
#                     all_tickets_df,
#                     use_container_width=True,
#                     hide_index=True,
#                     on_select="rerun",
#                     selection_mode="single-row",
#                 )

#                 selected_rows = event.selection.rows if event and event.selection else []
#                 if selected_rows:
#                     selected_row = all_tickets_df.iloc[selected_rows[0]]
#                     st.session_state.selected_ticket_id = int(selected_row["Ticket ID"])
#                 elif st.session_state.selected_ticket_id is None:
#                     st.session_state.selected_ticket_id = int(all_tickets_df.iloc[0]["Ticket ID"])

#                 st.markdown("---")
#                 st.subheader("Review & Action Center")

#                 current_ticket = get_ticket_by_id(st.session_state.selected_ticket_id)

#                 if current_ticket:
#                     st.info(f"Reviewing Ticket #{current_ticket[0]} submitted by {current_ticket[1]}")
#                     st.write(f"**Category:** {current_ticket[2]} | **Subject:** {current_ticket[3]}")
#                     st.text_area("Applicant's Original Message", value=current_ticket[4], disabled=True)

#                     with st.form("hr_processing_form"):
#                         updated_status = st.selectbox(
#                             "Update Status",
#                             ["Pending Review", "Action Taken", "Resolved"],
#                             index=["Pending Review", "Action Taken", "Resolved"].index(current_ticket[5])
#                             if current_ticket[5] in ["Pending Review", "Action Taken", "Resolved"]
#                             else 0,
#                         )
#                         updated_notes = st.text_area("Add HR Response / Resolution Notes", value=current_ticket[6])
#                         save_btn = st.form_submit_button("Submit")

#                     if save_btn:
#                         update_ticket(st.session_state.selected_ticket_id, updated_status, updated_notes)
#                         st.success(f"✅ Ticket #{st.session_state.selected_ticket_id} updated.")
#                         st.rerun()