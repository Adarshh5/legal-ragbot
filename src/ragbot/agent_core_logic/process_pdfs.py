from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings

from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv
# load_dotenv() 

# def clean_text(text):
#     return " ".join(text.split())

# splitter = RecursiveCharacterTextSplitter(
#     chunk_size=1000,
#     chunk_overlap=200,
#     separators=["\n\n", "\n", ".", " "],
# )

# sector_files = {
#     "Fundamental Rights": "fundamental_rights.pdf",
#     "Criminal Law": "criminal_law.pdf",
#     "Property & Land Disputes": "property_land.pdf",
#     "Family Law": "family_law.pdf",
#     "Labor & Employment": "labor_employment.pdf",
#     "Consumer Protection": "consumer_protection.pdf",
#     "Environmental Law": "environmental_law.pdf",
#     "Taxation": "taxation.pdf",
#     "Cyber Crimes": "cyber_crimes.pdf"
# }

# all_chunks = []
# for sector, filename in sector_files.items():
#     loader = PyPDFLoader(f"./data/{filename}")
#     pages = loader.load()

#     for page_num, page in enumerate(pages):
#         page.page_content = clean_text(page.page_content)  # <-- clean text here
#         chunks = splitter.split_documents([page])
#         for chunk in chunks:
#             chunk.metadata["source"] = sector
#             chunk.metadata["page_number"] = page_num + 1
#             all_chunks.append(chunk)

# embedding_model = OllamaEmbeddings(model='nomic-embed-text')

# vectorstore = Chroma(
#     persist_directory="./vector_db",
#     embedding_function=embedding_model
# )

# vectorstore.add_documents(all_chunks)
# vectorstore.persist()


from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Pinecone as PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec  # ✅ नए SDK से
from dotenv import load_dotenv
import os
from langchain_ollama import OllamaEmbeddings


load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
PINECONE_REGION = os.getenv("PINECONE_REGION")

# ✅ नया Pinecone क्लाइंट बनाओ:
pc = Pinecone(api_key=PINECONE_API_KEY)

# ✅ अगर index नहीं बना है तो नया बनाओ:
existing_indexes = [index['name'] for index in pc.list_indexes()]
print("अगर index नहीं बना है तो नया बनाओ:")
if PINECONE_INDEX_NAME not in existing_indexes:
    pc.create_index(
        name=PINECONE_INDEX_NAME,
        dimension=768,  # तुम्हारे index का dimension 1024 है (llama-text-embed-v2 से)
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws", 
            region=PINECONE_REGION
        )
    )
print("तुम्हारे index का dimension 768 है (llama-text-embed-v2 से)")
embedding_model = OllamaEmbeddings(model='nomic-embed-text')

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", ".", " "],
)

sector_files = {
    "Fundamental Rights": "fundamental_rights.pdf",
    "Criminal Law": "criminal_law.pdf",
    "Property & Land Disputes": "property_land.pdf",
    "Family Law": "family_law.pdf",
    "Labor & Employment": "labor_employment.pdf",
    "Consumer Protection": "consumer_protection.pdf",
    "Environmental Law": "environmental_law.pdf",
    "Taxation": "taxation.pdf",
    "Cyber Crimes": "cyber_crimes.pdf"
}

def clean_text(text):
    return " ".join(text.split())

all_chunks = []
for sector, filename in sector_files.items():
    loader = PyPDFLoader(f"./data/{filename}")
    pages = loader.load()

    for page_num, page in enumerate(pages):
        page.page_content = clean_text(page.page_content)
        chunks = splitter.split_documents([page])
        for chunk in chunks:
            chunk.metadata["source"] = sector
            chunk.metadata["page_number"] = page_num + 1
            all_chunks.append(chunk)

# ✅ LangChain PineconeVectorStore को पुराने pinecone.init से नहीं,
# बल्कि index_name और embedding से चलाओ:
vectorstore = PineconeVectorStore.from_documents(
    documents=all_chunks,
    embedding=embedding_model,
    index_name=PINECONE_INDEX_NAME,
    # Pinecone के नए क्लाइंट को host param नहीं चाहिए अगर आपने index AWS में सही region में बनाया है।
)

print("✅ Documents uploaded to Pinecone vector DB.")
