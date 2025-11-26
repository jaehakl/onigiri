from initserver import server
from routers import words, examples, user_texts, users, text_analysis

app = server()

app.include_router(words.router)
app.include_router(examples.router)
app.include_router(user_texts.router)
app.include_router(users.router)
app.include_router(text_analysis.router)
