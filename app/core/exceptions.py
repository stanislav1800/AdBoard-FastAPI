
from fastapi import HTTPException, status

UserIsNotPresentException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
)

InvalidRefreshTokenException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Недопустимый refresh token"
)

RefreshTokenExpiredException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Срок действия токена обновления истек"
)

TokenInvalidException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='Неверный токен',
)

UserNotAccessException = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail='Пользователь не имеет доступа',
)

PasswordsNotMatchException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='Пароли не совпадают',
)

IncorrectUsernameOrPasswordException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Incorrect username or password",
    headers={"WWW-Authenticate": "Bearer"},
)
InvalidAuthenticationCredentialsException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid authentication credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

UserAlreadyExistsException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail='Пользователь уже существует',
)

ChatNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Chat not found or access denied",
)

FailedCreateMessageException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Failed to create message",
)

UserNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Пользователя не существует",
)

UserNotCommentYourselfException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail = "Вы не можете себя оценивать",
)

ImageNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Изображение не найдено",
)

ListingNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Объявления не существует",
)

ListingAlreadyDeletedException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Объявление уже удалено",
)

ListingAlreadyModerateException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Объявление уже прошло модерацию",
)

ListingAlreadyFavoriteException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Объявление уже в избранном",
)
