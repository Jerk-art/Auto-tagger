import hashlib

def file_sha256(file_path):
    h = hashlib.sha256()

    with open(file_path, 'rb') as file:
        while True:
            chunk = file.read(h.block_size)
            if not chunk:
                break
            h.update(chunk)

    return h.hexdigest()
