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

    random.shuffle(pass_list)
    password = "".join(pass_list)

    # --- কপি বাটন এর জন্য এই অংশটি খেয়াল করুন ---
    st.write("### Your New Password:")
    
    # st.code ব্যবহার করলে টেক্সটটি কপি করার সুবিধা পাওয়া যায়
    st.code(password, language="") 
    
    st.success("Click the icon on the right side of the box to copy!")