import asyncio
import openai
import base64
from pdf2image import convert_from_path
import os
import io
from pathlib import Path
import time


async def extract_entities_from_image(image, page_num):
    start_time = time.time()

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    client = openai.AsyncOpenAI()
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract entities as JSON."},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{image_base64}"},
                    },
                ],
            }
        ],
        max_tokens=1000,
    )

    # Write response to individual JSON file
    filename = f"./datasets/page_{page_num}_entities.json"
    with open(filename, "w") as f:
        f.write(response.choices[0].message.content)

    end_time = time.time()


    # write time taken to a log file
    with open("./datasets/extraction_times.log", "a") as log_file:
        log_file.write(f"Page {page_num}: {end_time - start_time:.2f} seconds\n")

    return response.choices[0].message.content


async def main():
    # Convert PDF to images
    images = convert_from_path("./datasets/Laptop_Order_Invoice.pdf", dpi=200)

    end_page_to_process = 3  # process only first 3 pages for demo purposes
    results = await asyncio.gather(
        *[
            extract_entities_from_image(img, i + 1)
            for i, img in enumerate(images[:end_page_to_process])
        ]
    )

    # merge the results to one JSON, they are all from the same list of entities
    client = openai.AsyncOpenAI()
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Merge these JSON lists into one."
                        + "They are all from the same invoice.",
                    },
                    {
                        "type": "text",
                        "text": "\n".join(results),
                    },
                ],
            }
        ],
        max_tokens=1000,
    )

    merged_json = response.choices[0].message.content
    return merged_json



if __name__ == "__main__":
    start_overall = time.time()
    merged_json = asyncio.run(main())
    end_overall = time.time()
    with open("./datasets/extraction_times.log", "a") as log_file:
        log_file.write(
            f"Overall processing time: {end_overall - start_overall:.2f} seconds\n"
        )

    # Write to a new JSON file
    with open("./datasets/merged_entities.json", "w") as f:
        f.write(merged_json)
