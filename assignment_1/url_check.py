import re
import ipaddress
from urllib.parse import urlsplit

class URLValidator():
    ul = "\u00a1-\uffff"  # Unicode letters range (must not be a raw string).

    # IP patterns
    ipv4_re = (
        r"(?:0|25[0-5]|2[0-4][0-9]|1[0-9]?[0-9]?|[1-9][0-9]?)"
        r"(?:\.(?:0|25[0-5]|2[0-4][0-9]|1[0-9]?[0-9]?|[1-9][0-9]?)){3}"
    )
    ipv6_re = r"\[[0-9a-f:.]+\]"  # (simple regex, validated later)

    # Host patterns
    hostname_re = (
        r"[a-z" + ul + r"0-9](?:[a-z" + ul + r"0-9-]{0,61}[a-z" + ul + r"0-9])?"
    )
    # Max length for domain name labels is 63 characters per RFC 1034 sec. 3.1
    domain_re = r"(?:\.(?!-)[a-z" + ul + r"0-9-]{1,63}(?<!-))*"
    tld_re = (
        r"\."  # dot
        r"(?!-)"  # can't start with a dash
        r"(?:[a-z" + ul + "-]{2,63}"  # domain label
        r"|xn--[a-z0-9]{1,59})"  # or punycode label
        r"(?<!-)"  # can't end with a dash
        r"\.?"  # may have a trailing dot
    )
    host_re = "(" + hostname_re + domain_re + tld_re + "|localhost)"

    regex = re.compile(
        r"^(?:[a-z0-9.+-]*)://"  # scheme is validated separately
        r"(?:[^\s:@/]+(?::[^\s:@/]*)?@)?"  # user:pass authentication
        r"(?:" + ipv4_re + "|" + ipv6_re + "|" + host_re + ")"
        r"(?::[0-9]{1,5})?"  # port
        r"(?:[/?#][^\s]*)?"  # resource path
        r"\Z",
        re.IGNORECASE,
    )
    message = "Invalid URL."
    schemes = ["http", "https", "ftp", "ftps"]
    unsafe_chars = frozenset("\t\r\n")

    def __init__(self, schemes=None, **kwargs):
        super().__init__(**kwargs)
        if schemes is not None:
            self.schemes = schemes

    def __call__(self, value):
        if not isinstance(value, str):
            return self.message, 400
        if self.unsafe_chars.intersection(value):
            return self.message, 400
        # Check if the scheme is valid.
        scheme = value.split("://")[0].lower()
        if scheme not in self.schemes:
            return self.message, 400

        # Then check full URL
        try:
            splitted_url = urlsplit(value)
        except ValueError:
            return self.message, 400
        regex_matches = self.regex.search(str(value))
        if not regex_matches:
            return self.message, 400
        else:
            # Now verify IPv6 in the netloc part
            host_match = re.search(r"^\[(.+)\](?::[0-9]{1,5})?$", splitted_url.netloc)
            if host_match:
                potential_ip = host_match[1]
                try:
                    ipaddress.IPv6Address(potential_ip)
                except ValueError:
                    return self.message, 400

        # The maximum length of a full host name is 253 characters per RFC 1034
        # section 3.1. It's defined to be 255 bytes or less, but this includes
        # one byte for the length of the name and one byte for the trailing dot
        # that's used to indicate absolute names in DNS.
        if splitted_url.hostname is None or len(splitted_url.hostname) > 253:
            return self.message, 400

        return "", 200

# c = URLValidator()
# print(c("http://www.google.com")[1])
# print(c("http://abc:5555")[1])