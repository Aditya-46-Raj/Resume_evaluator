from grammar_check import check_grammar

text = "This are my resume. I has many skill like Python and Flask."
result = check_grammar(text)
for issue in result:
    print(issue)
