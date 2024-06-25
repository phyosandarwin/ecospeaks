import streamlit as st
import os
from openai import AzureOpenAI
import requests

st.set_page_config(page_title='NewsDigest', page_icon='🗞️', layout='centered')
st.logo('assets/logo.png')

# Load credentials
azure_api_key = st.secrets['azure']['AZURE_OPENAI_KEY']
azure_endpoint = st.secrets['azure']['AZURE_OPENAI_ENDPOINT']
azure_version = st.secrets['azure']['AZURE_OPENAI_API_VERSION']
newsapi_key = st.secrets['newsapi']['API_KEY']

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-35-turbo"

# Initialize session state keys
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "system", "content": "What environmental topic would you like to look up news on?"}]
if "questions" not in st.session_state:
    st.session_state["questions"] = None
if "previous_keyword" not in st.session_state:
    st.session_state["previous_keyword"] = None
if "summaries" not in st.session_state:
    st.session_state["summaries"] = None

# load client
client = AzureOpenAI(
    azure_endpoint=azure_endpoint,
    api_key=azure_api_key,
    api_version=azure_version,
)

system_prompt = """
You are an AI news summarizer and question generator.

Follow these steps to engage the user:

1. Request a Keyword: Ask the user for an environmental topic or keyword. If the user discusses a non-environmental topic, politely redirect them to an environmental keyword.

2. Return the article title, article summary and links. 
    - Summarize the content of the articles returned. The summaries **must be based on the source articles without speculations or assumptions**.
    - Number your summaries and include the article name and source.
    
3. Generate Quiz Questions: 
    Generate 3 quiz questions based on the summaries provided. Provide three possible answers per question:
    - There should be one correct answer and two incorrect answers.
    - Use linebreaks according to this template:
    {
        Question 1: <question>\n
        A: <first option>\n
        B: <second option>\n
        C: <third option>
    }

4. Evaluate Answers: 
- Check the user's answers using the summaries and explain any incorrect responses with clear reasoning.

Important Note: At any point in the conversation, if the user brings up a non-environmental topic, politely refuse and suggest they provide a relevant environmental keyword.
"""

st.header('Enviro-News Digest', divider='rainbow')
st.caption('Key in your environmental topic keyword. Read the summaries. Ask the chatbot to generate questions. Give your answers and view the returned feedback!')
with st.sidebar:
    st.header("About NewsDigest Chatbot")
    st.subheader("Model: GPT-3.5-Turbo")
    st.button("➕ New Chat", on_click=lambda: st.session_state.clear())
    with st.expander("System Prompt"):
        st.write(system_prompt)

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Function to fetch news headlines
def fetch_news_headlines(keyword):
    url = f'https://newsapi.org/v2/everything?q={keyword}&pageSize=10&searchIn=title&sortBy=relevancy,publishedAt&apiKey={newsapi_key}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        articles = data['articles']
        print("Articles:", articles)  # Print articles for debugging
        headlines = []
        for article in articles:
            if article['source']['name'] != '[Removed]' and article['title'] != '[Removed]':
                headline = {
                    'title': article['title'],
                    'url': article['url'],
                    'summary': article['description']
                }
                headlines.append(headline)
        return headlines[:3]  # Return up to 3 valid articles
    else:
        print(f"Error fetching news: {response.status_code}")
        return None

# Function to generate a response based on fetched headlines
def generate_response(news_headlines):
    if news_headlines:
        response = ""
        for idx, headline in enumerate(news_headlines, 1):
            response += f"{idx}. {headline['title']}\n"
            response += f"\nSummary: {headline['summary']}\n"
            response += f"\nLink: {headline['url']}\n\n"
        return response
    else:
        return "Sorry, I couldn't find any news related to that topic."

def generate_quiz_questions(summaries):
    prompt = f"Generate 3 quiz questions based on the following summaries:\n\n{summaries}"
    completion = client.chat.completions.create(
        model=st.session_state["openai_model"],
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content

def check_if_environmental_topic(text):
    # Use the AI model to evaluate if the text is related to environmental topics
    completion = client.chat.completions.create(
        model=st.session_state["openai_model"],
        messages=[
            {"role": "system", "content": "Check if text is related to environmental topics. Return 'yes' or 'no'."},
            {"role": "user", "content": text}
        ],
    )
    print(completion.choices[0].message.content)
    return completion.choices[0].message.content.strip().lower() == "yes"

def evaluate_answers(user_answers, summaries, questions):
    reasoning_prompt = f"Use the {summaries} to evaluate the {user_answers} to each of the question in {questions}. Explicitly state if the user answer is correct or not.\
                        If the user's answer is wrong, then explain what should be the correct answer. If user's answer is correct, congratulate the user."
    completion = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": "system", "content": reasoning_prompt},
                ]
            )
    reasoning = completion.choices[0].message.content
    return reasoning

# Accept user input
prompt = st.chat_input("Message...", key="unique_chat_input")
if prompt:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Check for keywords to generate quiz questions
    if "questions" in prompt.lower():
        summaries = st.session_state.get("summaries", "")
        if summaries:
            questions = generate_quiz_questions(summaries)
            st.session_state["questions"] = questions
            response = questions
        else:
            response = "No summaries available to generate quiz questions from."

    elif "evaluate" in prompt.lower() or "answers" in prompt.lower():
        summaries = st.session_state.get("summaries", "")
        questions = st.session_state.get("questions", "")
        user_answers = prompt.lower().split("answers: ")[1].strip().split(", ")
        if not user_answers:
            response = "You didn't provide any answers."
        else:
            response = evaluate_answers(user_answers, summaries, questions)

    else:
        # Check if the user's input is related to the environmental topic
        is_environmental_topic = check_if_environmental_topic(prompt)
        if is_environmental_topic:
            # Fetch news headlines and generate summaries for the new keyword
            st.session_state["previous_keyword"] = prompt
            news_headlines = fetch_news_headlines(prompt)
            response = generate_response(news_headlines)
            st.session_state["summaries"] = response
        else:
            response = f"Sorry, {prompt} is not an environmental topic. Please try again with a relevant environmental keyword."

    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})