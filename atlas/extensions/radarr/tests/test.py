
import re
import string


def main():
    test_cases = [
        "Hey Atlas, could you download me the movie Iron Man?",
        "Atlas, please download the movie Avengers for me.",
        "Atlas, download the movie Spider-Man for me, please.",
        "Atlas, I want to watch the movie Interstellar. Can you download it?",
        "Atlas, please download Avengers for me.",
        "Can you get Thor, Atlas?",
        "I'd like to watch Captain America, Atlas. Can you download it?",
        "Atlas, download Spider-Man for me, please.",
    ]

    #pattern = r"(?i)(movie|tv series|tv show|series|download me|download|get|watch|download it|download for me|download me)?\s*([^\,?]+)"
    #pattern = r"(?:movie|tv series|tv show|series|download me|download|get|watch|download it|download for me|download me)?\s*([^,?.]+)"
    pattern = r'(movie|tv series|tv show|series|download me the movie|download the movie|watch the movie|download|watch)(.*?)(\.|,|for|it|$)' 

    for test in test_cases:
        match = re.search(pattern, test)
        if match:
            print(f'{test}  :  {match.group(2).strip().rstrip(string.punctuation)}')
        else:
            print(f'{test}  :  None')
                
if __name__ == "__main__":
    main()