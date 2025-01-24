import json
import ollama

def make_llama_3_prompt(user, system="", assistant=""):
    system_prompt = ""
    if system:
        system_prompt = (
            f"<|start_header_id|>system<|end_header_id|>\n\n{system}<|eot_id|>"
        )
    
    user_prompt = f"<|start_header_id|>user<|end_header_id|>\n\n{user}<|eot_id|>"
    assistant_prompt = f"<|start_header_id|>assistant<|end_header_id|>\n\n{assistant}<|eot_id|>" if assistant else "<|start_header_id|>assistant<|end_header_id|>\n\n"
    
    return f"<|begin_of_text|>{system_prompt}{user_prompt}{assistant_prompt}"

def get_movie_schema():
    return """\
    0|Title|TEXT eg. "Inception"
    1|Director|TEXT eg. "Christopher Nolan"
    2|Year|INT eg. "2010"
    3|Rating|TEXT eg. "PG-13"
    4|Runtime|TEXT eg. "148 min" castable to int
    5|Genre|TEXT eg. "Sci-Fi"
    6|Box_Office|TEXT eg. "$829,895,144" and when null has a value "N/A"
    """

def generate_question_and_query():
    system = "You are a data analyst with 10 years of experience writing complex SQL queries.\n"
    system += (
        "Consider a table called 'movies' with the following schema (columns)\n"
    )
    system += get_movie_schema()
    system += "Consider the following questions, and queries used to answer them:\n"

    question = """What is the highest-grossing movie of all time?"""
    sql = "SELECT Title, Box_Office FROM movies WHERE Box_Office != 'N/A' ORDER BY CAST(REPLACE(Box_Office, ',', '') AS INTEGER) DESC LIMIT 1;"

    system += "Question: " + question + "\n"
    system += "Query: " + sql + "\n"

    user = "Write a question and a query that are similar but different to those above.\n"
    user += "Format the question and query as a JSON object, i.e.\n"
    user += '{"question" : str, "sql_query": str }.\n'

    user += "Make sure to only return me valid sqlite SQL query generated as response to the question. Don't give me any comments. Just return question and query as JSON objects. Make sure query is relevant to the question. Make sure each query is complete and ends with a ;\n"

    prompt = make_llama_3_prompt(user, system)

    # Generate the result from the model
    result = ollama.generate(model='mistral', prompt=prompt)

    # Inspect and parse the result['response']
    response_str = result['response']
    print("resualt========",result)
    print("response_str========",response_str)

    try:
        response_dict = json.loads(response_str)
    except json.JSONDecodeError as e:
        print("Failed to parse response as JSON:", e)
        response_dict = {}

    return response_dict

def save_to_jsonl(data, file_path):
    with open(file_path, 'a') as f:
        for entry in data:
            f.write(json.dumps(entry) + '\n')

def main():
    output_file_path = 'questions_queries.jsonl'
    num_iterations = 2  # Define how many questions and queries you want to generate
    all_questions_queries = []

    for _ in range(num_iterations):
        question_and_query = generate_question_and_query()
        all_questions_queries.append(question_and_query)
    print(all_questions_queries)
    save_to_jsonl(all_questions_queries, output_file_path)
    print(f"Saved {num_iterations} questions and queries to {output_file_path}")

# Execute the main function
if __name__ == "__main__":
    main()