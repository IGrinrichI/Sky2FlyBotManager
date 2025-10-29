from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
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


with open("private_key.pem", "rb") as key_file:
    private_key = serialization.load_pem_private_key(
        key_file.read(),
        password=None
    )

with open("public_key.pem", "rb") as key_file:
    public_key = serialization.load_pem_public_key(
        key_file.read()
    )


padding = padding.OAEP(
     mgf=padding.MGF1(algorithm=hashes.SHA256()),
     algorithm=hashes.SHA256(),
     label=None
)
encrypted = public_key.encrypt(b'I was walking through the forest with shovel.', padding)
print(encrypted)
text = input()
try:
    decrypted = private_key.decrypt(eval(f"b'{text}'"), padding)
except SyntaxError:
    decrypted = private_key.decrypt(eval(f'b"{text}"'), padding)
print(decrypted)
print(private_key.decrypt(private_key.public_key().encrypt(decrypted, padding), padding))



