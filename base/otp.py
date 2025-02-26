import pyotp

def gen_otp():
    totp = pyotp.TOTP(pyotp.random_base32(), interval=300)

    return totp.now()