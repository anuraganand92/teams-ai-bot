from openai import AzureOpenAI

from config import Config

config = Config()

aoi_client = AzureOpenAI(
    azure_endpoint = config.AZURE_OPENAI_ENDPOINT, 
    api_version = config.AZURE_OPENAI_VERSION, 
    api_key = config.AZURE_OPENAI_API_KEY
)

# Get image description from GPT-4o
def describe_image(img_url: str):

#   img_prompt = "A" 

  response = aoi_client.chat.completions.create(
    model="gpt-4o",
    messages=[
      {
            "role": "system",
            "content": [
            {"type": "text", "text": "You are a cute bot."}
            ]
        },
      {
        "role": "user",
        "content": [
          {"type": "text", "text": "Hey there!"},
        #   {
        #     "type": "image_url",
        #     "image_url": {
        #       "url": img_url,
        #     },
        #   },
        ],
      }
    ],
    # max_tokens=300,
  )

  return response.choices[0].message.content
print(describe_image("abcd"))