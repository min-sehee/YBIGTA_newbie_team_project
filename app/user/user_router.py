from fastapi import APIRouter, HTTPException, Depends, status
from app.user.user_schema import User, UserLogin, UserUpdate, UserDeleteRequest
from app.user.user_service import UserService
from app.dependencies import get_user_service
from app.responses.base_response import BaseResponse

user = APIRouter(prefix="/api/user")


@user.post("/login", response_model=BaseResponse[User], status_code=status.HTTP_200_OK)
def login_user(user_login: UserLogin, service: UserService = Depends(get_user_service)) -> BaseResponse[User]:
    try:
        user = service.login(user_login)
        return BaseResponse(status="success", data=user, message="Login Success.") 
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"message": str(e)})


@user.post("/register", response_model=BaseResponse[User], status_code=status.HTTP_201_CREATED)
def register_user(user: User, service: UserService = Depends(get_user_service)) -> BaseResponse[User]:
    ## TODO
    """
    사용자의 회원가입을 처리하는 함수

    Args:
        user (User): 등록할 사용자의 정보
        service (UserService, optional): 사용자 관련 기능을 처리하는 서비스 인스턴스

    Raises:
        HTTPException: 등록할 이메일이 이미 존재하는 경우

    Returns:
        BaseResponse[User]: 회원가입 성공 시 사용자 정보 반환
    """
    try:
        new_user = service.register_user(user)
        return BaseResponse(status="success", data=new_user, message="User registeration success.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"message": str(e)})


@user.delete("/delete", response_model=BaseResponse[User], status_code=status.HTTP_200_OK)
def delete_user(user_delete_request: UserDeleteRequest, service: UserService = Depends(get_user_service)) -> BaseResponse[User]:
    ## TODO
    """
    사용자를 삭제 처리하는 함수

    Args:
        user_delete_request (UserDeleteRequest): 삭제할 사용자의 정보
        service (UserService, optional): 사용자 관련 기능을 처리하는 서비스 인스턴스

    Raises:
        HTTPException: 사용자의 이메일을 찾을 수 없는 경우

    Returns:
        BaseResponse[User]: 삭제된 사용자의 정보를 반환
    """
    try:
        deleted_user = service.delete_user(user_delete_request.email)
        return BaseResponse(status="success", data=deleted_user, message="User Deletion Success.")
    except ValueError as e:
        raise HTTPException(status_code=404, detail={"message": str(e)})


@user.put("/update-password", response_model=BaseResponse[User], status_code=status.HTTP_200_OK)
def update_user_password(user_update: UserUpdate, service: UserService = Depends(get_user_service)) -> BaseResponse[User]:
    ## TODO
    """
    사용자의 비밀번호를 변경하는 함수

    Args:
        user_update (UserUpdate): 비밀번호 변경 요청 정보
        service (UserService, optional): 사용자 관련 기능을 처리하는 서비스 인스턴스

    Raises:
        HTTPException: 사용자의 이메일을 찾을 수 없는 경우

    Returns:
        BaseResponse[User]: 비밀번호 변경 성공 시 사용자 정보 반환
    """
    try:
        updated_user = service.update_user_pwd(user_update)
        return BaseResponse(status="success", data=updated_user, message="User password update success.")
    except ValueError as e:
        raise HTTPException(status_code=404, detail={"message": str(e)})
