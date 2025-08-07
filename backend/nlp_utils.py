import language_tool_python
import textstat

def get_cover_letter_feedback(text):
    tool = language_tool_python.LanguageTool('en-US')

    # 1. Grammar & Spelling Check
    matches = tool.check(text)
    grammar_issues = [tool.get_message(match) for match in matches]

    # 2. Readability Score
    readability = textstat.flesch_reading_ease(text)

    # 3. Sentence/Tone Summary
    word_count = len(text.split())
    sentence_count = text.count('.') + text.count('!') + text.count('?')
    avg_sentence_length = word_count / sentence_count if sentence_count else 0

    # 4. Suggestions
    feedback = {
        "grammar_issues": grammar_issues[:5],  # limit to top 5
        "readability_score": readability,
        "average_sentence_length": avg_sentence_length,
        "word_count": word_count,
        "suggestions": []
    }

    if readability < 60:
        feedback["suggestions"].append("Consider simplifying your language to improve readability.")
    if avg_sentence_length > 20:
        feedback["suggestions"].append("Try using shorter sentences for better clarity.")

    return feedback
