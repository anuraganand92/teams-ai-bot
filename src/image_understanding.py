from openai import AzureOpenAI

from .config import Config

config = Config()

aoi_client = AzureOpenAI(
    azure_endpoint = config.AZURE_OPENAI_ENDPOINT, 
    api_version = config.AZURE_OPENAI_VERSION, 
    api_key = config.AZURE_OPENAI_API_KEY
)

# Get image description from GPT-4o
async def describe_image(img_url: str):

  img_prompt = "Describe each aspect of the image in great detail. Be thorough in your response. \
                Return the image description in a neatly formatted response. \
                Do not format the headings of a section using ###<heading>###. \
                Instead, divide each section with 2 consecutive new lines characters, and with 1 new line character between the heading and its content." 

  response = aoi_client.chat.completions.create(
    model="gpt-4o",
    messages=[
      {
        "role": "user",
        "content": [
          {"type": "text", "text": img_prompt},
          {
            "type": "image_url",
            "image_url": {
              "url": img_url,
            },
          },
        ],
      }
    ],
    # max_tokens=300,
  )

  return response.choices[0].message.content