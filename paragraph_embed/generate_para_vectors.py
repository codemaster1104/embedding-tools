import openai
import sys
import os
import time

API_BASE_URL = "https://llama.us.gaianet.network/v1"
MODEL_NAME = "llama"
API_KEY = "GAIA"

def summarize(source_text):
    client = openai.OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "Respond with a comprehensive summary of the text in the user message"},
            {"role": "user", "content": source_text},
        ],
        model=MODEL_NAME,
        stream=False,
    )
    return chat_completion.choices[0].message.content

def qgen(source_text):
    client = openai.OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "Respond with a list of 5 questions. The text in the user message must contain specific answers to each question. Each question must be complete without references to unclear context such as \"this team\" or \"that lab\". Each question must be on its own line. Just list the questions without any introductory text or numbers."},
            {"role": "user", "content": source_text},
        ],
        model=MODEL_NAME,
        stream=False,
    )
    return chat_completion.choices[0].message.content

def agen(source_text, question):
    client = openai.OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": f"Give a comprehensive and well-reasoned answer to the user question strictly based on the context below.\n{source_text}"},
            {"role": "user", "content": question},
        ],
        model=MODEL_NAME,
        stream=False,
    )
    return chat_completion.choices[0].message.content

def process_chunk(chunk):
    results = []
    results.append(f"{summarize(chunk)}")
    
    questions = qgen(chunk).splitlines()
    for q in questions:
        if q.strip():
            answer = agen(chunk, q)
            results.append(f"Q: {q}\nA: {answer}")
    
    return "\n".join(results)

def remove_empty_lines(text):
    return "\n".join(line for line in text.splitlines() if line.strip())

def format_time(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 script.py input.txt output.txt")
        sys.exit(1)

    input_file, output_file = sys.argv[1], sys.argv[2]

    with open(input_file, 'r') as f:
        content = f.read()

    content = remove_empty_lines(content)

###################################### adjust chunk size here ######################################
    chunk_size = 1000
#####################################################################################################

    chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
    total_chunks = len(chunks)

    print(f"Total chunks to process: {total_chunks}")

    start_time = time.time()
    with open(output_file, 'w') as f:
        for i, chunk in enumerate(chunks):
            chunk_start_time = time.time()
            
            processed_chunk = process_chunk(chunk)
            processed_chunk = remove_empty_lines(processed_chunk)
            f.write(processed_chunk + "\n\n")

            chunk_end_time = time.time()
            chunk_duration = chunk_end_time - chunk_start_time

          
            if i == 0:
                estimated_total_time = chunk_duration * total_chunks
                print(f"Estimated total time: {format_time(estimated_total_time)}")

            # Update progress
            chunks_left = total_chunks - (i + 1)
            estimated_time_left = chunk_duration * chunks_left
            progress = (i + 1) / total_chunks * 100

            print(f"\rProgress: {progress:.2f}% | Estimated time remaining: {format_time(estimated_time_left)}", end="")

    end_time = time.time()
    total_duration = end_time - start_time

    print(f"\nProcessing complete. Total time taken: {format_time(total_duration)}")
    print(f"Output written to {output_file}")

if __name__ == "__main__":
    main()