import openai
from dotenv import load_dotenv
from time import sleep
import os

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
OPENAI_RETRY_COUNT = 5

SITUATION = """
You are an editor at 'The Tech Times', an expert journalist for cutting-edge tech News.
I will give you the raw text content.
You must provide a concise summary in mutually exclusive but collectively complete sentences.
Please understand that some comments may include sarcasm, and you must figure out that it's not the central argument or factual.

You should not be politically biased. Always maintain professionalism.
You must be able to write in a neutral tone, and not be biased towards any political party.
Avoid any political or religious statements at all costs, especially because some comments will diverge and may include such statements.

There is one exception, and that is when the article's title starts with 'Ask HN:' or 'Tell HN:'.
In such case, there is no article, and the text is the comments.
In that case, you must focus on the comments.

You must understand that the primary readers of this post are experts in the field, and they do not want to read the same thing they already know.
You must consider this question: What is the most important thing people should know about this post? Why is this post special? Is there something new or exciting thing going on? Did something get released? Why is this post, out of all the posts on Hacker News, suddenly getting so much attention? What made such tech-savvy people suddenly interested in this post? Your job is to capture vital points that interest the readers.
Do not repeat dull facts, such as 'The post is about a new technology'.

If some comments state a noticable key points, you must include them, but you must make it clear that 'an HN user points out that...', and that is not the main point of the article.

You must also know that you should be 'confident but not arrogant'.
It would be best not to use expressions like "this may be..." "potentially,"... or such.
Things should be 'clearly' and 'obviously' stated.
"""


def shorten(text: str, limit: int, title="") -> str:
    summary = ""
    try:
        words = text.split()
        chunks = [" ".join(words[i : i + limit]) for i in range(0, len(words), limit)]
        for idx, w in enumerate(chunks):
            print("Summarizing (" + str(idx + 1) + "/" + str(len(chunks)) + f") {title}...")
            sleep(1)  # OpenAI has a rate limit of 60 requests per minute for pay-as-you-go users
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": f"""
{SITUATION}
                        
Hard limit {limit // 16} words.
Please understand that some comments may include sarcasm, and you must realize it's not the main point.
If a profound, arcane word aptly describes the sentence, utilize it to make the sentence shorter.

Text: {w}
""",
                    }
                ],
            )
            summary += completion["choices"][0]["message"]["content"]
        text = summary
    except Exception as e:
        print(f"Cannot summarize, error: {e}")
        new_text = text.split(".")
        new_text = ".".join(new_text[: 4 * len(new_text) // 5])  # 80% of the text
        return shorten(new_text, limit, title)
    print(f"Shortened {title} to {len(text.split())} tokens")
    return text


def bulletpoint_summarize(title, text):
    summary = ""
    try:
        print(f"Creating Summary for... {title}")
        sleep(1)  # OpenAI has a rate limit of 60 requests per minute for pay-as-you-go users
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": f"""
{SITUATION}
                    
Use markdown syntax wherever possible, such as making quotes, bold texting, or in-line codes.
It must be a freeform text, not bullet points.
It must be grammatically correct and polite.
Each sentence must end with punctuation, such as a period.
The title of this post is '{title}'.

These are the HN Comments. The comments may digress from the main point.
You must ignore the digression, and focus on the main points of the article,
unless the digression is relevant to the article or article is unaccessible.
Focus on the first part of the text, since those are the articles; the most important part.

Now, I will give you the text.
Summarize in markdown, less than 100 tokens, end with a period for each sentence.
Text: {text}
""",
                },
            ],
        )
        summary = completion["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Cannot summarize: {title}, trying again with shorter text... error: {e}")
        new_text = text.split(".")
        new_text = ".".join(new_text[: 4 * len(new_text) // 5])
        return bulletpoint_summarize(title, new_text)
    return summary


def summarize_hn_comments(title, text):
    summary = ""
    try:
        print(f"Creating Summary for... {title}")
        sleep(1)  # OpenAI has a rate limit of 60 requests per minute for pay-as-you-go users
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": f"""
{SITUATION}

Use markdown syntax wherever possible, such as making quotes, bold texting, or in-line codes.
It must be a freeform text, not bullet points.
It must be grammatically correct and polite.
Each sentence must end with punctuation, such as a period.
The title of this post is '{title}'.

Now, I will give you the text.
Summarize in markdown, less than 100 tokens, end with a period for each sentence.

Text: {text}
""",
                },
            ],
        )
        summary = completion["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Cannot summarize: {title}, trying again with shorter text... error: {e}")
        new_text = text.split(".")
        new_text = ".".join(new_text[: 4 * len(new_text) // 5])
        return summarize_hn_comments(title, new_text)
    return summary


def title_format(title):
    title = title.strip()
    title = title.replace("’", "'")
    title = title.replace("“", '"')
    title = title.replace("”", '"')
    title = title.replace("‘", "'")
    title = title.replace(" and ", " & ")
    title = title.replace(" And ", " & ")
    title = title.replace(" AND ", " & ")
    if title[-1] == ".":
        title = title[:-1]
    if title[0] == '"' and title[-1] == '"':
        title = title[1:-1]
    if title[0] == "'" and title[-1] == "'":
        title = title[1:-1]
    return title


def get_title(title, text):
    try:
        print(f"Finding a better title... {title}")
        for _ in range(OPENAI_RETRY_COUNT):
            sleep(1)  # OpenAI has a rate limit of 60 requests per minute for pay-as-you-go users
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": f"""
{SITUATION}

Capitalize in Chicago style.
You must keep the proper nouns, acronyms, scientific terms, and registered trademarks as is, such as 'iCloud', 'macOS', 'GPT', 'US', 'FBI', 'EU', 'CFTC', 'LLMs', 'GPTs', 'HN', 'Q&A', 'OpenPGP', 'SSH', 'PDF', 'PH.D.', '$3M', and so on.
Do not add suffixes, such as '| Website'.
Ignore the Website saying You Need JavaScript; That's not the important part.
No period in the end.
Please understand that some comments may include sarcasm, and you must realize it's not the main point.
The original title was {title}.
HARD LIMIT 15 WORDS.
Text: {text}

What would be a better title for this post?
""",
                    },
                ],
            )
            title = completion["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Cannot get title: {title}, trying again with shorter text... error: {e}")
        new_text = text.split(".")
        new_text = ".".join(new_text[: 4 * len(new_text) // 5])
        return get_title(title, new_text)
    return title_format(title)
