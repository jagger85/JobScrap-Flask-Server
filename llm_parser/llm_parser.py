from groq import Groq

client = Groq()


def parse_llm(content):
    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {
                "role": "system",
                "content": "collect all the job relevant data and organize it in a table",
            },
            {"role": "user", "content": f"{content}"},
        ],
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=True,
        stop=None,
    )

    for chunk in completion:
        print(chunk.choices[0].delta.content or "", end="")
