from datetime import datetime

def encode_field(name: str, value: str | int | float | bool | datetime):
   # format data as Label:Type:Value
# ex: encode_field("age", 18) -> b'age:int:18'
# joins everything into one string
    data_string = name + ':' + type(value).__name__ + ':' + str(value)
    
    #  Encode: Converts text to bytes for the SHA-256 line:  
    #     hashlib.sha256(data).digest() is used for sha256 takes data in bytes
    return data_string.encode('utf-8')