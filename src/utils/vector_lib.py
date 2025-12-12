"""
Vector library for the application.
"""

import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

load_dotenv()


def get_local_index(name: str):
    """
    Returns the local index for the given name.
    """

    index_dir = f"storage/vectors/{name.lower()}_index"
    embeddings = HuggingFaceEmbeddings(model_name=os.getenv("EMBEDDING_MODEL"))
    return FAISS.load_local(index_dir, embeddings, allow_dangerous_deserialization=True)
