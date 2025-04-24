from langchain_community.document_loaders import PyPDFLoader
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore

pdf_path = Path(__file__).parent / "nodejs.pdf"
loader = PyPDFLoader(file_path=pdf_path)
# this loader loads the whole pdf in an array of documents

docs = loader.load()

print(docs)


# text_splitter = RecursiveCharacterTextSplitter(
#     chunk_size=1000,
#     chunk_overlap=200
# )

# split_docs = text_splitter.split_documents(
#     documents=docs
# )


# embedder = GoogleGenerativeAIEmbeddings(google_api_key="AIzaSyBfbdVV0YNmWCK2p5q_qnWzKHwdMlu0T5s", model="models/text-embedding-004")

# # vectore_store = QdrantVectorStore.from_documents(
# #     documents=[],
# #     url="http://localhost:6333",
# #     collection_name="learning_langchain",
# #     embedding=embedder,
# # )

# # vectore_store.add_documents(documents=split_docs)
# # print("injection done!!")

# # Till here everything is done to inject the documents into the vector store 

# # now retrival 
# retriver = QdrantVectorStore.from_existing_collection(
#     url="http://localhost:6333",
#     collection_name="learning_langchain",
#     embedding=embedder,
    
# )

# search_results = retriver.similarity_search(
#     query="what is nodejs exactly? ",
# )

# print("relevant chunks : " , search_results)

# #then do the system prompt and all of that stuff 
# system_prompt = f"""
# you are an helpful ai assistant that is used to answer questions . 

# context : {search_results}
# """