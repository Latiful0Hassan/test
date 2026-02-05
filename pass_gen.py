import streamlit as st
import random
import string
from st_copy_to_clipboard import st_copy_to_clipboard

st.title("Python Shikder's Password Generator 🔐")

# সেশন স্টেট সেটআপ (পাসওয়ার্ড ধরে রাখার জন্য)
if "generated_password" not in st.session_state:
    st.session_state.generated_password = ""

lower = string.ascii_lowercase
upper = string.ascii_uppercase
num = string.digits
special_char = string.punctuation

pass_len = st.slider("Select Password Length:", 4, 16, 8)
pass_mode = st.selectbox("Select Complexity:", ["Easy", "Medium", "Hard"])

if st.button("Generate Password"):
    pass_list = []
    if "Easy" in pass_mode:
        pass_list.extend([random.choice(lower), random.choice(num)])
        chars = lower + num
    elif "Medium" in pass_mode:
        pass_list.extend([random.choice(lower), random.choice(upper), random.choice(num)])
        chars = lower + upper + num
    else:
        pass_list.extend([random.choice(lower), random.choice(upper), random.choice(num), random.choice(special_char)])
        chars = lower + upper + num + special_char

    while len(pass_list) < pass_len:
        pass_list.append(random.choice(chars))

    random.shuffle(pass_list)
    st.session_state.generated_password = "".join(pass_list)

# পাসওয়ার্ড দেখানোর অংশ
if st.session_state.generated_password:
    st.write("### Your Password:")
    st.code(st.session_state.generated_password, language="")
    
    # এই বাটনটি মোবাইল ফ্রেন্ডলি
    from st_copy_to_clipboard import st_copy_to_clipboard
    st_copy_to_clipboard(st.session_state.generated_password)