from pathlib import Path
import re

def go():
    tweet_file = open("input.txt", "w")
    try:
        read_all_files(tweet_file)
    finally:
        tweet_file.close()

def read_all_files(tweet_file):
    files = Path("RAW_TWEETS").glob("*.txt")
    for file in files:
        read_file(file, tweet_file)
        
def clean_tweet(tweet):
    return re.sub(r"\s+", ' ', tweet).strip()
        
def read_file(file_name, tweet_file):
    print(f"reading file: {file_name}")
    file = open(file_name, "r")
    try:
        saved_line = ""
        for line in file:
            if re.match(r"\d+ repl(y|ies) \d+ retweets? \d+ likes?", line):
                if saved_line:
                    tweet_file.write(saved_line + "\n")
            else:
                cleaned = clean_tweet(line)
                if cleaned:
                    saved_line = cleaned
                
    finally:
        file.close()
    
if __name__ == '__main__':
    go()
