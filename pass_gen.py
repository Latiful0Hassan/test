import streamlit as st
import random
import string

st.title("Python Shikder's Password Generator 🔐")

# ১. সেশন স্টেট চেক করা (পাসওয়ার্ড ধরে রাখার জন্য)
if "generated_password" not in st.session_state:
    st.session_state.generated_password = ""

lower = string.ascii_lowercase
upper = string.ascii_uppercase
num = string.digits
special_char = string.punctuation

pass_len = st.slider("Select Password Length:", 4, 16, 8)
pass_mode = st.selectbox("Select Complexity:", ["Easy", "Medium", "Hard"])

# ২. জেনারেট বাটন
if st.button("Generate Password"):
    pass_list = []
    if "Easy" in pass_mode:
        pass_list.append(random.choice(lower)); pass_list.append(random.choice(num))
        chars = lower + num
    elif "Medium" in pass_mode:
        pass_list.append(random.choice(lower)); pass_list.append(random.choice(upper)); pass_list.append(random.choice(num))
        chars = lower + upper + num
    else:
        pass_list.extend([random.choice(lower), random.choice(upper), random.choice(num), random.choice(special_char)])
        chars = lower + upper + num + special_char

    while len(pass_list) < pass_len:
        pass_list.append(random.choice(chars))

    random.shuffle(pass_list)
    # পাসওয়ার্ডটি সেশন স্টেটে সেভ করে রাখা
    st.session_state.generated_password = "".join(pass_list)

# ৩. পাসওয়ার্ড যদি জেনারেট হয়ে থাকে তবেই নিচের অংশ দেখাবে
if st.session_state.generated_password:
    st.write("### Your Password:")
    st.code(st.session_state.generated_password, language="")

    # ৪. কপি বাটন
    if st.button("📋 Copy to Clipboard"):
        st.copy_to_clipboard(st.session_state.generated_password)
        # কপি হয়েছে কিনা বোঝার জন্য টোস্ট মেসেজ
        st.toast(f"Copied: {st.session_state.generated_password}", icon="✅")