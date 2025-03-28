from fastapi import APIRouter

router = APIRouter(
    tags=['User Router 👥'],
    prefix="/user"
)


@router.get("/")
def main():
    return {"message": "Welcome to the User Router 👥"}
