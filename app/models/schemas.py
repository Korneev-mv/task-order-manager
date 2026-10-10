from pydantic import BaseModel, field_validator, Field
class UserCreate(BaseModel):
    name: str
    email: str
    password: str = Field(..., min_length=8, max_length=72)

class UserRegister(BaseModel):
    name: str
    email: str
    password: str = Field(..., min_length=8, max_length=72)

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

class OrderCreate(BaseModel):
    amount: float = Field(gt=0)

class OrderResponse(BaseModel):
    id: int
    user_id: int
    amount: float
    created_at: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class CalculateItem(BaseModel):
    a: float
    b: float
    operation: str

    @field_validator('operation')
    def validate_operation(cls, v):
        return v.lower()


class TaskCreate(BaseModel):
    title: str
    description: str = Field(default=None)
    status: str = Field(default="todo")

    @field_validator('status')
    def validate_status(cls, v):
        if v not in ['todo', 'in_progress', 'done']:
            raise ValueError('Status must be in "todo", "in_progress", "done"')
        return v

class TaskUpdate(BaseModel):
    title: str = Field(default=None)
    description: str = Field(default=None)
    status: str = Field(default=None)

    @field_validator('status')
    def validate_status(cls, v):
        if v is not None and v not in ['todo', 'in_progress', 'done']:
            raise ValueError('Status must be in "todo", "in_progress", "done"')
        return v

class TaskResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str | None = None
    status: str
    created_at: str
    updated_at: str

class UserTasksStats(BaseModel):
    user_id: int
    name: str
    tasks_done: int

class CalculationError(ValueError):
    pass

class DivisionByZeroError(CalculationError):
    pass

class UnknownOperationError(CalculationError):
    pass