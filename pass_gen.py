import streamlit as st
import random
import string

# টাইটেল এবং ডিজাইন
st.title("Python Shikder's Password Generator 🔐")
st.subheader("Generate a secure password instantly!")

lower = string.ascii_lowercase
upper = string.ascii_uppercase
num = string.digits
special_char = string.punctuation

# ১. ওয়েব পেজে ইনপুট নেওয়ার অংশ (Slider এবং Selectbox)
pass_len = st.slider("Select Password Length:", min_value=4, max_value=16, value=8)
pass_mode = st.selectbox("Select Complexity:", ["Easy (Small + Num)", "Medium (Small + Cap + Num)", "Hard (Everything)"])

# ২. জেনারেট বাটন
if st.button("Generate Password"):
    pass_list = []
    
    # মোড অনুযায়ী লজিক
    if "Easy" in pass_mode:
        pass_list.append(random.choice(lower))
        pass_list.append(random.choice(num))
        all_chars = lower + num
    elif "Medium" in pass_mode:
        pass_list.append(random.choice(lower))
        pass_list.append(random.choice(upper))
        pass_list.append(random.choice(num))
        all_chars = lower + upper + num
    else: # Hard mode
        pass_list.append(random.choice(lower))
        pass_list.append(random.choice(upper))
        pass_list.append(random.choice(num))
        pass_list.append(random.choice(special_char))
        all_chars = lower + upper + num + special_char

    # ৩. পাসওয়ার্ড পূর্ণ করা
    while len(pass_list) < pass_len:
        pass_list.append(random.choice(all_chars))

    random.shuffle(pass_list)
    password = "".join(pass_list)

    # ৪. ফলাফল দেখানো
    st.success(f"Your Generated Password: `{password}`")
    st.info("Copy the password above.")