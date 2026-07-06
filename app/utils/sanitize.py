def sanitize_text(value: str, max_length: int = 200) -> str:
    cleaned = value.strip()
    if len(cleaned) > max_length:
        return cleaned[:max_length]
    return cleaned
