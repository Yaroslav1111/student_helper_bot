# rag_system/processor.py
import os
import asyncio
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA

os.makedirs("data/vector_storage", exist_ok=True)
os.makedirs("data/uploaded_files", exist_ok=True)

# Инициализируем компоненты LangChain
embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
llm = ChatOpenAI(model_name="gpt-4o", openai_api_key=os.getenv("OPENAI_API_KEY"))
VECTORSTORE_PATH = "data/vector_storage"

def _process_document_sync(file_path: str, course_id: str):
    """Синхронная функция для обработки, чтобы запускать в отдельном потоке."""
    print(f"Processing {file_path} for course {course_id}...")
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)
    
    course_vectorstore_path = os.path.join(VECTORSTORE_PATH, f"course_{course_id}")
    vector_store = Chroma.from_documents(
        documents=texts, 
        embedding=embeddings,
        persist_directory=course_vectorstore_path
    )
    vector_store.persist()
    print("Processing complete.")

async def process_document(file_path: str, course_id: str):
    """Асинхронный запуск обработки документа в отдельном потоке."""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _process_document_sync, file_path, course_id)

def get_qa_chain(course_id: str):
    course_vectorstore_path = os.path.join(VECTORSTORE_PATH, f"course_{course_id}")
    if not os.path.exists(course_vectorstore_path):
        return None
        
    vector_store = Chroma(persist_directory=course_vectorstore_path, embedding_function=embeddings)
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(),
        return_source_documents=False
    )
    return qa_chain