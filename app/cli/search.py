from app.core.database import ChromaAdapter
def search_knowledge():
    knowledge_db:ChromaAdapter = ChromaAdapter()
    query = ""
    while query != "exit" or query != "q":
        query = input("请输入查询内容: ")
        for d in knowledge_db.query(query):
            print(d.page_content)
            print("----------------")
