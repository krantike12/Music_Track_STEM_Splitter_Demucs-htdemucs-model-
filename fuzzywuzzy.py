from fuzzywuzzy import fuzz

def match_text(text1, text2):
    print(f"Comparing '{text1}' and '{text2}'")
    print(f"Similarity ratio: {fuzz.ratio(text1, text2)}")
    return fuzz.ratio(text1, text2)

match_text("Bansa Community and Resource Center!", "Bansa Community and Resource Center!")