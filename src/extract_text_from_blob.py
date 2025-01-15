from io import BytesIO
import pdfplumber
from langchain_core.documents import Document
from .image_understanding import describe_image

async def extract_text(response, file_type):
    blob_content=[]
    # For txt file
    if file_type=='txt':
        try:
            text = response.content
            blob_content.append(Document(page_content=text))
        except:
            raise Exception("Couldn't get content from the text file")

    # For pdf file
    elif file_type=='pdf':
        try:
            bytes_object = response.content
            stream = BytesIO(bytes_object)
            with pdfplumber.open(stream) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    # Extract text or structured data from each page
                    text = page.extract_text()
                    document = Document(
                                        page_content=text,
                                        metadata={"page": page_num}
                                    )
                    blob_content.append(document)  # Each page's text is treated as a separate document
        except:
            raise Exception("Couldn't get content from the PDF file")
    # For image file
    elif file_type in ["image", "png", "jpeg", "jpg", "tiff", "svg", "heic", "webp", "gif"]:
        img_url = response
        img_desc = await describe_image(img_url)
        blob_content.append(Document(page_content=img_desc))
    # For other file types
    else:
        blob_content = None
        
    return blob_content
