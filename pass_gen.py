import streamlit as st
import random
import string

# টাইটেল
st.title("Python Shikder's Password Generator 🔐")

lower = string.ascii_lowercase
upper = string.ascii_uppercase
num = string.digits
special_char = string.punctuation

# ইনপুট
pass_len = st.slider("Select Password Length:", min_value=4, max_value=16, value=8)
pass_mode = st.selectbox("Select Complexity:", ["Easy (Small + Num)", "Medium (Small + Cap + Num)", "Hard (Everything)"])

if st.button("Generate Password"):
    pass_list = []
    
    if "Easy" in pass_mode:
        pass_list.append(random.choice(lower))
        pass_list.append(random.choice(num))
        current_all_chars = lower + num
    elif "Medium" in pass_mode:
        pass_list.append(random.choice(lower))
        pass_list.append(random.choice(upper))
        pass_list.append(random.choice(num))
        current_all_chars = lower + upper + num
    else: 
        pass_list.append(random.choice(lower))
        pass_list.append(random.choice(upper))
        pass_list.append(random.choice(num))
        pass_list.append(random.choice(special_char))
        current_all_chars = lower + upper + num + special_char

    while len(pass_list) < pass_len:
        pass_list.append(random.choice(current_all_chars))

# ... (পাসওয়ার্ড জেনারেট করার আগের লজিক একই থাকবে) ...

    random.shuffle(pass_list)
    password = "".join(pass_list)

    st.write("### Your New Password:")
    
    # ১. পাসওয়ার্ডটি বক্সে দেখান (মোবাইল ইউজাররা এখানে ট্যাপ করেও কপি করতে পারবে)
    st.code(password, language="") 
    
    # ২. সরাসরি একটি 'Copy' বাটন যোগ করা (যা মোবাইলে সবসময় দেখা যাবে)
    if st.button("📋 Copy to Clipboard"):
        st.copy_to_clipboard(password)
        st.toast("Password copied to clipboard!", icon="✅")