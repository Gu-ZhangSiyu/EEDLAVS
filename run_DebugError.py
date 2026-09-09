class ImagekaError(Exception):
    # Error base class.
    pass

def safe_open(path, mode="r"):
    try:
        return open(path, mode)
    except Exception as e:
        raise ImagekaError(f"Unable to read file {path!r}: {e}")
