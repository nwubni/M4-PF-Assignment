"""
This script is used to build the data pipeline for the RAG system
"""

from datetime import datetime, timezone
import os
import sys
import uuid

from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


def build_index(document_path: str, index_dir: str = None):
    """
    Build a FAISS index from a document with metadata.

    Args:
        document_path (str): Path to the document to index.
        index_dir (str, optional): Directory to save the index. If None, derives from document filename.
                                  Format: storage/vectors/{filename}_index/
    """
    # Extract filename from document path and create index directory name
    if index_dir is None:
        # Get the base filename without extension (e.g., "TechAgent.txt" -> "TechAgent")
        document_filename = os.path.splitext(os.path.basename(document_path))[0]
        # Convert to lowercase and create index directory path
        index_dir = f"storage/vectors/{document_filename.lower()}_index"
    
    if not os.path.exists(index_dir):
        os.makedirs(index_dir, exist_ok=True)

    # Load document
    loader = TextLoader(document_path)
    documents = loader.load()

    # Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200, length_function=len
    )
    chunks = text_splitter.split_documents(documents)

    document_id = os.path.splitext(os.path.basename(document_path))[0]
    for idx, chunk in enumerate(chunks):
        chunk.metadata.update(
            {
                "id": str(uuid.uuid4()),
                "document_id": document_id,
                "chunk_index": idx,
                "token_count": len(chunk.page_content.split()),
                "char_count": len(chunk.page_content),
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        )

    # Create embeddings and vector store
    embeddings = HuggingFaceEmbeddings(
        model_name=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
        model_kwargs={"device": "cuda" if os.getenv("USE_CUDA") == "true" else "cpu"},
    )

    # Create and save chunk embeddings in vector store
    vector_store = FAISS.from_documents(chunks, embeddings)
    vector_store.save_local(index_dir)

    print(f"Index built and saved to {index_dir}")
    print(f"Total chunks created: {len(chunks)}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m src.build.index path/to/document.txt")
        sys.exit(1)

    build_index(sys.argv[1])