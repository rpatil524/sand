from urllib.parse import urlparse

value = str(value).strip()
parsedurl = urlparse(value)
if parsedurl.scheme == "" and parsedurl.netloc == "":
    # not a valid URL, convert to empty string so that if missing_values is set (typically to empty string)
    # it will be interpreted as missing value and ignored
    return ""
return value
