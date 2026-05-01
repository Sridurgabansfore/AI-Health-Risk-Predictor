def summarize_text(text):
    # This is a very simple mock summarizer.
    # In a real app, you might use a library like 'transformers' or 'sumy'.
    words = text.split()
    if len(words) > 10:
        return " ".join(words[:10]) + "..."
    return text
