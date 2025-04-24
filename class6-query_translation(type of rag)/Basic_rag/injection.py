
# print(response.choices[0].message)

from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import os
from langchain_qdrant import QdrantVectorStore
from openai import OpenAI

load_dotenv()
 
pdf_path = Path(__file__).parent / "data" / "nodejs.pdf"
loader = PyPDFLoader(pdf_path)

docs = loader.load()

# print(docs)


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)


split_docs = text_splitter.split_documents(
    documents=docs
)

embedder = GoogleGenerativeAIEmbeddings(google_api_key="AIzaSyBfbdVV0YNmWCK2p5q_qnWzKHwdMlu0T5s", model="models/text-embedding-004")

vectore_store = QdrantVectorStore.from_documents(
    documents=split_docs,
    url="http://localhost:6333",
    collection_name="learning_langchain",
    embedding=embedder,
)

vectore_store.add_documents(documents=split_docs)
print("injection done!!")


