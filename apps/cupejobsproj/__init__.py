__version_info__ = {
    "major": 1,
    "minor": 2,
    "micro": 0,
    "releaselevel": "alpha",
    "serial": 0,
}


def get_version(short=False):
    assert __version_info__["releaselevel"] in (
        "alpha",
        "beta",
        "release candidate",
        "final",
    )
    vers = [
        "%(major)i.%(minor)i" % __version_info__,
    ]
    if __version_info__["micro"]:
        vers.append(".%(micro)i" % __version_info__)
    if __version_info__["releaselevel"] != "final" and not short:
        if len(__version_info__["releaselevel"].split(" ")) > 1:
            str1, str2 = __version_info__["releaselevel"].split(" ")
            vers.append("%s%s%i" % (str1[0], str2[0], __version_info__["serial"]))
        else:
            vers.append(
                "%s%i"
                % (
                    __version_info__["releaselevel"][0],
                    __version_info__["serial"],
                )
            )
    return "".join(vers)


__version__ = get_version()
