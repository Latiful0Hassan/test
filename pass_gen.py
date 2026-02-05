import random
import string

lower = string.ascii_lowercase
uppper = string.ascii_uppercase
num = string.digits
special_char = string.punctuation

while True:
    try:
        pass_len = int(input("Please Choose Your Password Length (4-16): "))
        if pass_len <4 or pass_len >16:
            print("Password Should Be 4 to 16 Characters.")
            continue
        break
    except ValueError:
        print("Please Enter An Integer Number.")
        
while True:
    pass_mode = input("For Easy (E), Medium (M) or Hard (H): ").lower()
    pass_list = []
    if pass_mode == 'e':
        pass_list.append(random.choice(lower))
        pass_list.append(random.choice(num))
        all_chars = lower + num
        break
    elif pass_mode == 'm':
        pass_list.append(random.choice(lower))
        pass_list.append(random.choice(uppper))
        pass_list.append(random.choice(num))
        all_chars = lower + uppper + num
        break
    elif pass_mode == 'h':
        pass_list.append(random.choice(lower))
        pass_list.append(random.choice(uppper))
        pass_list.append(random.choice(num))
        pass_list.append(random.choice(special_char))
        all_chars = lower + uppper + num + special_char
        break
    else:
        print("Invalid Mode.")
        continue

while len(pass_list) < pass_len:
    pass_list.append(random.choice(all_chars))

random.shuffle(pass_list)
password = "".join(pass_list)
print(password)
        
        
        