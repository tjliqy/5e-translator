from app.core.database import ChromaAdapter
from app.core.transform.mysql_transformer import get_proofread_words, is_nessesary_embedding, word_to_document

def transform_proofread():
    adapter = ChromaAdapter()
    documents = []
    for word in get_proofread_words():
        if is_nessesary_embedding(word):
            documents.append(word_to_document(word))
    adapter.add(documents)
