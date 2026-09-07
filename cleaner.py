def clean_ascii(text: str) -> str:

    if not text:
        return ""

    return (
        str(text)
        .encode("ascii", "ignore")
        .decode("ascii")
        .strip()
    )