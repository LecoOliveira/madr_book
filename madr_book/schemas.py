from pydantic import BaseModel, ConfigDict, EmailStr


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class Message(BaseModel):
    message: str


class LivroSchema(BaseModel):
    ano: str
    titulo: str
    autor_id: int


class LivroPublic(LivroSchema):
    id: int


class LivroList(BaseModel):
    livros: list[LivroPublic]


class LivroUpdate(BaseModel):
    ano: str | None = None
    titulo: str | None = None


class RomancistaSchema(BaseModel):
    nome: str


class RomancistaPublic(RomancistaSchema):
    id: int
