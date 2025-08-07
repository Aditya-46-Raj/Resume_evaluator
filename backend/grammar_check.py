# backend/grammar_check.py
import language_tool_python

def check_grammar(text):
    tool = language_tool_python.LanguageTool('en-US')
    matches = tool.check(text)
    result = []

    for match in matches:
        result.append({
            "message": match.message,
            "error": text[match.offset:match.offset + match.errorLength],
            "suggestions": match.replacements,
            "start": match.offset,
            "end": match.offset + match.errorLength
        })

    return result
