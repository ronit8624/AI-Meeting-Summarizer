from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os


def get_llm():

    return ChatMistralAI(
        model="mistral-small-latest",
        mistral_api_key=os.getenv("MISTRAL_API_KEY"),
        temperature=0.2,
    )


def split_transcript(transcript: str):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=3000,
        chunk_overlap=200,
    )

    return splitter.split_text(transcript)


def summarize(transcript: str):

    llm = get_llm()

    chunks = split_transcript(transcript)

    map_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
You are an expert AI content summarizer.

The transcript may belong to:
- a meeting
- a podcast
- a speech
- a trailer
- a movie dialogue
- an interview
- a YouTube video

Your job:
- understand the actual context first
- summarize naturally
- NEVER say "meeting" unless it is actually a meeting
- DO NOT generate HTML
- DO NOT generate markdown code blocks
- Use clean bullet points
- Keep the summary readable and professional
            """
        ),
        ("human", "{text}"),
    ])

    map_chain = map_prompt | llm | StrOutputParser()

    partial_summaries = []

    for chunk in chunks:

        response = map_chain.invoke({
            "text": chunk
        })

        partial_summaries.append(response)

    combined_text = "\n\n".join(partial_summaries)

    final_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
Create one final clean summary.

Rules:
- No HTML
- No markdown code blocks
- No fake assumptions
- If this is a trailer/speech/video, summarize accordingly
- Use headings and bullet points naturally
- Keep it concise but insightful
            """
        ),
        ("human", "{text}"),
    ])

    final_chain = final_prompt | llm | StrOutputParser()

    return final_chain.invoke({
        "text": combined_text
    })


def generate_title(transcript: str):

    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
Generate a SHORT natural title based on the transcript.

Rules:
- Maximum 6 words
- No HTML
- No markdown
- No quotes
- No extra explanation
- Detect context properly
- If it's a movie trailer, create cinematic title
- If it's a speech, create speech-like title
- If it's a meeting, create professional meeting title
            """
        ),
        ("human", "{text}"),
    ])

    chain = prompt | llm | StrOutputParser()

    title = chain.invoke({
        "text": transcript[:2000]
    })

    return title.strip()