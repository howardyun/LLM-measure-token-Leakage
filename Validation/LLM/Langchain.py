import os
from langchain_community.llms import OpenAI

os.environ["OPENAI_API_KEY"] = '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'
# llm = OpenAI(model_name="gpt-4o-mini",max_tokens=1024)
# llm("怎么评价人工智能")
# from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),  # This is the default and can be omitted
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Say this is a test",
        }
    ],
    model="gpt-4o",
)




