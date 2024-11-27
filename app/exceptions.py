from fastapi import status, HTTPException

ForbiddenException = HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Недостаточно прав доступа')
RoleNotFoundException = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Роль не найдена')
ActionNotFoundException = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Дейстиве не найдено')