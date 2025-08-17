from langchain_ollama import OllamaEmbeddings

from langchain_community.document_loaders import PyPDFLoader

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

from langchain_community.vectorstores import Pinecone as PineconeVectorStore
from langchain_community.document_loaders import PyPDFLoader
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import os

# Load env
load_dotenv()

# Load ENV variables
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
PINECONE_REGION = os.getenv("PINECONE_REGION")

# Embedding model
embedding_model = OpenAIEmbeddings(model='text-embedding-3-small')
# Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY)

# ✅ Connect to existing index
vectorstore = PineconeVectorStore.from_existing_index(
    index_name=PINECONE_INDEX_NAME,
    embedding=embedding_model
)


def clean_text(text):
    return " ".join(text.split())


def process_document(file_path, sector_name):
    loader = PyPDFLoader(file_path)
    pages = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " "],
    )

    all_chunks = []
    for page_num, page in enumerate(pages):
        page.page_content = clean_text(page.page_content)
        chunks = splitter.split_documents([page])

        for chunk in chunks:
            chunk.metadata["source"] = sector_name
            chunk.metadata["page_number"] = page_num + 1
            all_chunks.append(chunk)

    return all_chunks


file_path = "./data/taxation.pdf"
sector_name = "Taxation"

new_chunks = process_document(file_path, sector_name)

# ✅ Upload to Pinecone
vectorstore.add_documents(new_chunks)

print(f"✅ Document '{sector_name}' added to Pinecone vector DB.")
