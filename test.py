from openai import OpenAI

client = OpenAI(
    api_key='sk-proj-fGYknLfFHKPSM3KvkEHNT3BlbkFJunfNyAfGlx136ouZEztM'
)

completion = client.completions.create(model='curie', promt='answer')
print(completion.choices[0].text)
print(dict(completion).get('usage'))
print(completion.model_dump_json(indent=2))
