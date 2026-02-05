import streamlit as st
import random
import string
from st_copy_to_clipboard import st_copy_to_clipboard # নতুন লাইব্রেরি

st.title("Python Shikder's Password Generator 🔐")

# সেশন স্টেট সেটআপ
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

# পাসওয়ার্ড দেখানোর এবং কপি করার অংশ
if st.session_state.generated_password:
    st.write("### Your Password:")
    
    # এটি পাসওয়ার্ডটি একটি বক্সে দেখাবে
    st.code(st.session_state.generated_password, language="")
    
    # এটি সেই ম্যাজিক বাটন যা মোবাইলে সরাসরি কপি করবে
    st_copy_to_clipboard(st.session_state.generated_password)
    
    st.info("Click the 'Copy' button above to save your password.")