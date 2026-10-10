import httpx
from fastapi import HTTPException, APIRouter

router = APIRouter()

@router.get("/github/{username}")
async def get_github_user(username: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"https://api.github.com/users/{username}", headers={"Authorization": "token YOUR_GITHUB_TOKEN"})
            response.raise_for_status()
            data = response.json()

            return {
                "login": data["login"],
                "name": data["name"],
                "followers": data["followers"],
                "public_repos": data["public_repos"]
            }

        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Network error")
        except httpx.HTTPStatusError:
            raise HTTPException(status_code=404, detail="User not found")
