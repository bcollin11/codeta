import zipfile

def extract (path, extpath):
  if zipfile.is_zipfile(path):
    zipf = zipfile.ZipFile(path)
    zipf.extractall(extpath)
  else:
    return None

