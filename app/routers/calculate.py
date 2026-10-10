from app.models.schemas import DivisionByZeroError, UnknownOperationError, CalculateItem
from fastapi import HTTPException, APIRouter

router = APIRouter()

@router.get("/hello")
async def main():
    return {"message": "Hello World"}

def calculate(a: float, b: float, operation: str) -> float:
    if operation == "add":
        result = a + b
    elif operation == "sub":
        result = a - b
    elif operation == "mul":
        result = a * b
    elif operation == "div":
        if b == 0:
            raise DivisionByZeroError("Division by zero")
        result = a / b
    else:
        raise UnknownOperationError("Non correct operation")
    return result

@router.post("/calculate/")
async def calculate_func(item: CalculateItem):
    try:
        result = calculate(item.a, item.b, item.operation)
        return {"result": result}
    except DivisionByZeroError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except UnknownOperationError as e:
        raise HTTPException(status_code=422, detail=str(e))
