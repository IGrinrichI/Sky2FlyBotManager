import os
import sys
import time

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
# private_key = rsa.generate_private_key(
#     public_exponent=65537,
#     key_size=4096,
# )
# public_key = private_key.public_key()
#
#
# private_pem = private_key.private_bytes(
#     encoding=serialization.Encoding.PEM,
#     format=serialization.PrivateFormat.PKCS8,
#     encryption_algorithm=serialization.NoEncryption()
# )
#
# with open('private_key.pem', 'wb') as f:
#     f.write(private_pem)
#
# public_pem = public_key.public_bytes(
#     encoding=serialization.Encoding.PEM,
#     format=serialization.PublicFormat.SubjectPublicKeyInfo
# )
# with open('public_key.pem', 'wb') as f:
#     f.write(public_pem)
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def get_trial_time(key):
    try:
        with open(resource_path("private_key.pem"), "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None
            )

        pd = padding.OAEP(
             mgf=padding.MGF1(algorithm=hashes.SHA256()),
             algorithm=hashes.SHA256(),
             label=None
        )
        decrypted = private_key.decrypt(key, pd)
        # try:
        #     decrypted = private_key.decrypt(eval(f"b'{key}'"), pd)
        # except SyntaxError:
        #     decrypted = private_key.decrypt(eval(f'b"{key}"'), pd)

        trial_time = float(decrypted.decode('utf8'))
        return trial_time
    except Exception as e:
        return -1


if __name__ == '__main__':
    with open(resource_path("private_key.pem"), "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None
        )
    pd = padding.OAEP(
         mgf=padding.MGF1(algorithm=hashes.SHA256()),
         algorithm=hashes.SHA256(),
         label=None
    )
    public_key = private_key.public_key()
    encrypted = public_key.encrypt(str(time.time() + 3600 * 24 * 365).encode('utf8'), pd)
    print(encrypted)

    with open('key', 'wb') as f:
        f.write(encrypted)
    # decrypted = private_key.decrypt(encrypted, pd)
    # print(decrypted)
