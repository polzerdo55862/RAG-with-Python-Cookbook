#!/usr/bin/env python
# coding: utf-8

# ## Chapter 8 Evaluating RAG Systems

# ### Creating Synthetic Data for Automated Testing

# In[3]:


"""
Retrieves source documents for synthetic data creation.

This function fetches a collection of text passages from the 'rag-mini-wikipedia' 
dataset available on Hugging Face. These passages are utilized to generate 
synthetic question-answer pairs, which aid in assessing the effectiveness 
of Retrieval-Augmented Generation (RAG) systems.

Returns:
    docs_list (list): A list containing text passages prepared for synthetic 
                        data generation.
"""
# tag::pepare_source_synthetic_data[]
# Example usage
import pandas as pd

df = pd.read_parquet(
    "hf://datasets/rag-datasets/rag-mini-wikipedia/data/"
    "passages.parquet/part.0.parquet"
)

docs_list = df.passage.to_list()
# end::pepare_source_synthetic_data[]


# In[4]:


print(f"Number of documents: {len(docs_list)}")
print(f"List of docs:{docs_list}")


# In[5]:


"""
This function generates synthetic question-answer pairs from a list of documents.
It leverages a language model to create questions that are factual and answerable from the given context,
along with their corresponding answers. This synthetic data can be used to evaluate the performance of RAG systems.

Args:
    docs_list (list): A list of text documents from which to generate question-answer pairs.

Returns:
    question_answer_pairs (list): A list of dictionaries, where each dictionary contains a question, its answer,
    and the context from which they were derived.
"""
# tag::create_synthetic_question_answer_pairs[]
from pydantic import BaseModel

QA_generation_prompt = """
    Your task is to generate a question and its corresponding answer based on the 
    provided context.

    The question should be:
    - Direct and focused, seeking a specific factual piece of information present 
        in the context.
    - Formulated as a natural query a user might input into a search engine.
    - Independent of the context, meaning it should not contain phrases like 
        "according to the passage" or "in the context".

    The answer should be:
    - A concise and accurate response directly extracted or inferred from the context.

    Present your output in the following format:

    Output:
    Question: (Your concise, fact-based question)
    Answer: (The direct answer to the question)

    Context: {context}\n
    Output:"""
# end::create_synthetic_question_answer_pairs[]


# In[ ]:


# tag::create_synthetic_question_answer_pairs_complete[]
from openai import OpenAI
from pydantic import Field
import random

# Initialize the OpenAI client with your API key
client = OpenAI()

class QuestionAnswerPairs(BaseModel):
    question: str = Field(description="A factoid question about the context.")
    answer: str = Field(description="The answer to the factoid question.")

question_answer_pairs = []

random_text_chunks = random.sample(docs_list, 5)

for text_chunk in random_text_chunks:
    # generate hypothetical questions using the GPT-4 model
    completion = client.beta.chat.completions.parse(
        messages=[
            {
                "role": "user",
                "content": QA_generation_prompt.format(context=text_chunk),
            }
        ],
        model="gpt-4o",
        response_format=QuestionAnswerPairs,
    )

    question_answer_pair = completion.choices[0].message.parsed.model_dump()
    question_answer_pair["context"] = text_chunk
    question_answer_pairs.append(question_answer_pair)
# end::create_synthetic_question_answer_pairs_complete[]


# In[7]:


question_answer_pairs


# ### Evaluating the Retriever step by calculating the Context Precision@k

# In[8]:


# tag::calculate_relevance_example_prompt[]
question = "What is the capital of France?"
answer = "The capital of France is Paris."
retrieved_contexts = ["""France, a country in Western Europe, is known for its capital city, 
    Paris, which is a major European city and a global center for art, fashion, 
    and culture.""",
    """Paris is the capital city of France and is renowned for its historical landmarks 
    such as the Eiffel Tower and the Louvre Museum.""",
    """The Amazon rainforest is the world's largest tropical rainforest, spanning 
    across nine South American countries and supporting immense biodiversity."""
]
# end::calculate_relevance_example_prompt[]


# In[9]:


# tag::create_context_relevance_verification[]
from textwrap import dedent
from pydantic import BaseModel, Field
from openai import OpenAI

def context_relevance_verification(question, answer, retrieved_contexts):
    # Pydantic model for verification
    class Verification(BaseModel):
        reason: str = Field(..., description="Reason for verification")
        verdict: int = Field(..., description="Binary (0/1) verdict of verification")

    # Define the prompt for context relevance verification
    context_relevance_prompt = dedent('''
        Given a question, an answer, and a context, verify if the context
        was instrumental in deriving the given answer. Provide a detailed reason
        for your assessment and a binary verdict: "1" if the context is useful 
        and "0" if it is not.

        Input:
        Question: "{question}",
        Answer: "{answer}",
        Context: "{context}"
        ''')

    list_of_verifications = []

    # Iterate through each question-answer pair and its context
    for retrieved_context in retrieved_contexts:
        prompt = context_relevance_prompt.format(
                question=question, 
                answer=answer, 
                context=retrieved_context)

        client = OpenAI()
        completion = client.beta.chat.completions.parse(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="gpt-4o",
            response_format=Verification,
        )

        verification = completion.choices[0].message.parsed.model_dump()
        verification["question"] = question
        verification["answer"] = answer
        verification["retrieved_context"] = retrieved_context

        list_of_verifications.append(verification)
    return list_of_verifications

# end::create_context_relevance_verification[]


# In[10]:


list_of_verifications = context_relevance_verification(
                                    question, 
                                    answer,
                                    retrieved_contexts
                                )
list_of_verifications


# With the list of verdicts we can now calculate the context precision, which is the proportion of relevant chunks in the retrieved_contexts.

# In[11]:


# tag::calculate_context_relevance_score[]
import pandas as pd

def calculate_context_relevance_score(list_of_verifications):
    verdict_list = pd.DataFrame(list_of_verifications)["verdict"].to_list()

    denominator = sum(verdict_list) + 1e-10
    numerator = sum(
        [
            (sum(verdict_list[: i + 1]) / (i + 1)) * verdict_list[i]
            for i in range(len(verdict_list))
        ]
    )
    score = numerator / denominator # e.g. score = 0.999999
    return score
# end::calculate_context_relevance_score[]


# Let's apply the function to calculate the context relevance.

# In[12]:


score = calculate_context_relevance_score(list_of_verifications)
score


# ### Evaluating RAG systems using LLMs as a judge and the Faithfulness Metrics

#     """
#     Decomposes the sentences in an answer into simpler, unambiguous statements.
# 
#     Args:
#         question: The original question.
#         answer: The answer to be decomposed.
#         client: An initialized OpenAI client.
# 
#     Returns:
#         A list of decomposed statements.
#     """

# In[13]:


# tag::decompose_question_answer[]
from textwrap import dedent
from pydantic import BaseModel, Field
from openai import OpenAI

def decompose_answer(question: str, answer: str) -> list[str]:
    # Initialize the OpenAI client
    client = OpenAI()

    statement_prompt = """
    Given a question and an answer, analyze the complexity of each sentence 
    in the answer. Break down each sentence into one or more fully 
    understandable statements. Ensure that no pronouns or ambiguous references 
    are used in any statement. Output the decomposed statements as a list of strings.

    Question: {question}
    Answer: {answer}
    """

    prompt = statement_prompt.format(question=question, answer=answer)

    class Statements(BaseModel):
        """Structured response for statement extraction."""

        statements: list[str] = Field(description="List of decomposed statements.")

    completion = client.beta.chat.completions.parse(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-4o",
        response_format=Statements,
    )

    statements = completion.choices[0].message.parsed.statements
    return statements
# end::decompose_question_answer[]


# In[14]:


# tag::decompose_question_answer_run[]
question = """Describe the geographical extent and ecological significance of the 
Amazon rainforest."""

answer = dedent("""
The Amazon rainforest, the world's largest tropical rainforest, covers significant 
territory across nine South American countries. This vast area is renowned for 
its immense biodiversity, supporting millions of different plant and animal species. 
While it plays a crucial role in the global climate by absorbing substantial amounts 
of carbon dioxide, its impact on the overall oxygen production of the Earth is often 
overstated.
""")
# end::decompose_question_answer_run[]


# In[15]:


statements = decompose_answer(question, answer)

print("Decomposed Statements:")
for idx, stmt in enumerate(statements, 1):
    print(f"{idx}. {stmt}")


# Sobald wir eine Liste von statements haben, können wir nun die Statements mit dem context vergleichen. Wir vergleichen jedes der Statements mit dem retrieved text, und prüfen, ob die statements in der Antwort tatsächlich aus dem retrieved text kommen, oder das LLM einfach selbst den fakt eingestreut hat.

# In[16]:


# tag::faithfulness_judgement[]
from pydantic import BaseModel, Field
from textwrap import dedent
from openai import OpenAI

def judge_faithfulness(statements: list[str], context: str) -> list[dict]:

    # Initialize the OpenAI client
    client = OpenAI()

    faithfulness_judge_prompt = dedent(
        """
        Your task is to judge the faithfulness of a statement based on the 
        given context. You must return a verdict as 1 if the statement can 
        be directly inferred from the context, or 0 if the statement cannot 
        be directly inferred. Explain your reasoning.

        Context:
        {context}

        Statement:
        {statement}

        Answer:::
        Reason: (Explain your reasoning)                    
        Verdict: (1 or 0)
        """
    )

    class StatementFaithfulness(BaseModel):
        """Structured response for statement extraction."""

        statements: str = Field(description="Decomposed statement.")
        reason: str = Field(description="Reasoning for the faithfulness judgement.")
        verdict: int = Field(
                        description="1 if the statement is faithful, 0 otherwise."
                        )

    prompt = faithfulness_judge_prompt.format(statement=statement, context=context)

    completion = client.beta.chat.completions.parse(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-4o",
        response_format=StatementFaithfulness,
    )

    statement_faithfulness = completion.choices[0].message.parsed.model_dump()
    return statement_faithfulness

# end::faithfulness_judgement[]

# tag::faithfulness_judgement_run[]
statements_faithfulness = []

context = dedent(
    """
    The Amazon rainforest is the largest tropical rainforest in the world, 
    covering parts of nine South American countries. It is known for its 
    incredible biodiversity, housing millions of species of plants, insects, 
    birds, and other animals. The forest plays a crucial role in regulating 
    the Earth's climate by absorbing vast amounts of carbon dioxide.
    """
)

for statement in statements:
    statement_faithfulness = judge_faithfulness(
        statements=[statement], context=context
    )
    # Append the statement faithfulness to the list
    statements_faithfulness.append(statement_faithfulness)
# end::faithfulness_judgement_run[]


# In[17]:


"""
This function retrieves source documents for synthetic data creation. It fetches a collection of text passages from the 'rag-mini-wikipedia' dataset available on Hugging Face. These passages are utilized to generate synthetic question-answer pairs, which aid in assessing the effectiveness of Retrieval-Augmented Generation (RAG) systems.

Returns:
    docs_list (list): A list containing text passages prepared for synthetic data generation.
"""


# In[18]:


print("Number of statements:", len(statements_faithfulness))
statements_faithfulness


# The faithfulness score evaluates the alignment of statements with their corresponding context. It is calculated as the mean of individual statement scores derived from faithfulness judgments. The input, `statements_faithfulness`, is a list of dictionaries containing the faithfulness verdict for each statement. The resulting score, expressed as a float, represents the proportion of statements that are faithful to the provided context.
# 

# In[19]:


# tag::calculate_faithfulness_score[]
import pandas as pd

statements_faith_df = pd.DataFrame(statements_faithfulness)

number_of_claims = len(statements_faith_df["verdict"])  # 7
number_of_claims_in_context = statements_faith_df["verdict"].sum()  # 6
faithfulness_percentage = (
    number_of_claims_in_context / number_of_claims
) * 100
# end::calculate_faithfulness_score[]


# In[20]:


faithfulness_percentage


# ### RAG evaluation using Response Relevancy

# We will test the approach with the following example:

# In[21]:


# tag::calculate_response_relecancy_example[]
user_input="What is the capital of France?"
response="The capital of France is Paris."
# end::calculate_response_relecancy_example[]


# Now we just need a prompt that evaluates the relevance of the response by generating artificial questions that the response would answer and determining if the response is noncommittal.
# 
# We get back a list with LLM-generated questions and an assessment of whether the response is noncommittal. A response is considered noncommittal if it is evasive, vague, or ambiguous, such as "I don't know," "Maybe," or "It depends."

# In[22]:


# tag::response_relevance_assessment_prompt[]
from textwrap import dedent

response_relevance_prompt = dedent("""
    Generate three relevant question for the following answer 
    and indicate if the answer is noncommittal.

    Output:
    Question: [Generated Question]
    Noncommittal (1=Yes, 0=No): [0 or 1]

    An answer is considered noncommittal if it is evasive, vague, or ambiguous 
    (e.g., "I don't know," "Maybe," "It depends").

    Answer: {response}
    """)
# end::response_relevance_assessment_prompt[]


# To ensure we reliably return a list of dictionaries in the same format, we define an appropriate prompt template. Here, we use the class `GeneratedQuestions`, which contains objects of the class `GeneratedQuestion`.

# In[23]:


# tag::reponse_relevance_response_template[]
from pydantic import BaseModel, Field

prompt = response_relevance_prompt.format(response=response)

class GeneratedQuestion(BaseModel):
    question: str = Field(description="Generated question.")
    noncommittal: int = Field(
        description="1 if the answer is noncommittal, 0 otherwise."
    )

class GeneratedQuestions(BaseModel):
    questions: list[GeneratedQuestion] = Field(
        description="List of generated questions and their noncommittal status."
    )

client = OpenAI()

completion = client.beta.chat.completions.parse(
    messages=[
        {
            "role": "user",
            "content": prompt,
        }
    ],
    model="gpt-4o",
    response_format=GeneratedQuestions,
)

generated_questions = completion.choices[0].message.parsed.model_dump()["questions"]
# end::reponse_relevance_response_template[]


# In[24]:


generated_questions


# In the next step, we generate an embedding vector for all generated questions. Then, we calculate the cosine similarity between all artificially created questions and the real user input.
# 
# *Steps to Calculate Relevance of Generated Questions to User's Question
# 
# 1. If all generated questions are empty, return `NaN`.
# 2. If any generated question is noncommittal, return `0`.
# 3. Otherwise, calculate the cosine similarity between the user's question and the generated questions.
# 

# First, we define the function to calculate the embedding vector for the original question and the questions generated by the LLM. We use again the `text-embedding-3-small` model from OpenAI.

# In[25]:


# tag::calculate_embeddings_used_for_relevance_score[]
from openai import OpenAI

client = OpenAI()

def create_embeddings(text_chunk, client):
    embed_model = "text-embedding-3-small"
    embedding = (
        client.embeddings.create(input=[text_chunk], model=embed_model)
        .data[0]
        .embedding
    )
    return embedding
# end::calculate_embeddings_used_for_relevance_score[]


# In[26]:


user_input


# In[27]:


user_question_embedding = create_embeddings(user_input, client)
cosine_sims = []


# Now we apply the function to the user question and all LLM-generated questions, calculate the embedding vectors, and then compute the cosine similarity between the vectors.

# In[28]:


# tag::calculate_embeddings_run[]
import numpy as np
import pandas as pd

user_question_embedding = create_embeddings(user_input, client)
cosine_sims = []

for generated_question in generated_questions:
    generated_question["embedding"] = create_embeddings(
        generated_question["question"], client
    )

    generated_question["cosine_sim"] = np.dot(
        user_question_embedding, generated_question["embedding"]
    ) / (
        np.linalg.norm(user_question_embedding)
        * np.linalg.norm(generated_question["embedding"])
    )
# end::calculate_embeddings_run[]


# In[29]:


generated_question


# Finally, we calculate the relevance score as the mean of all computed cosine similarities. The higher the similarity, the better.
# 
# A similarity score close to 1 indicates that the two vectors are identical or point in the same direction, meaning the semantic meaning of both questions is very similar. Theoretically and mathematically, the score can become negative, which is rare with embedding models unless the embeddings are poorly trained or the texts are intentionally dissimilar. Assuming a range from 0 to 1, a value close to 1 is considered very good. How good is "good enough" depends, of course, on your specific RAG system and dataset. At the very least, it gives you an indication of whether changes to the RAG system have a positive or negative impact.

# In[30]:


# tag::calculate_relevance_score[]
# calculate the mean cosine similarity over all generated questions
cosine_sim_mean = pd.DataFrame(generated_questions)["cosine_sim"].mean()

# check if any of the generated questions are non-committal
committal = any(pd.DataFrame(generated_questions)["noncommittal"])

# if any of the generated questions are non-committal, set the score to 0
response_relevance_score = cosine_sim_mean * int(not committal)
# end::calculate_relevance_score[]


# In[31]:


response_relevance_score


# In[32]:


from openevals.prompts import CORRECTNESS_PROMPT

