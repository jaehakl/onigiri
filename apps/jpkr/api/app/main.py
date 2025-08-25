from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import JSONResponse
from initserver import server
from typing import Optional

# Add this import for the actor service

#from service.github_service import GitHubService, get_files_from_public_repo, get_file_content_from_public_repo

app = server()


#@app.get("/github/files/{owner}/{repo}")
#async def get_github_files(owner: str, repo: str, path: str = ""):
#    return get_files_from_public_repo(owner, repo, path)
#
#@app.get("/github/content/{owner}/{repo}")
#async def get_github_file_content(owner: str, repo: str, path: str):
#    return {"content": get_file_content_from_public_repo(owner, repo, path)}
#
#@app.get("/github/search")
#async def search_github_repos(query: str, limit: int = 10):
#    github_service = GitHubService()
#    return github_service.search_repositories(query, limit)
#
#@app.get("/github/repo/{owner}/{repo}")
#async def get_github_repo_info(owner: str, repo: str):
#    github_service = GitHubService()
#    return github_service.get_repository_info(owner, repo)