from app.user.user_repository import UserRepository
from app.user.user_schema import User, UserLogin, UserUpdate

class UserService:
    def __init__(self, userRepoitory: UserRepository) -> None:
        self.repo = userRepoitory

    def login(self, user_login: UserLogin) -> User:
        """
        등록된 사용자의 정보들을 바탕으로 로그인하는 메소드

        Args:
            - user_login (User): 로그인할 사용자의 정보

        Returns:
            - (User): 로그인된 사용자의 정보
        """

        user = self.repo.get_user_by_email(user_login.email)
        
        if not user:
            raise ValueError("User not Found.")
        
        if user.password != user_login.password:
            raise ValueError("Invalid ID/PW")

        return user
        
    def register_user(self, new_user: User) -> User:
        """
        새로운 사용자의 정보(email, password, username)를 등록하는 메소드

        Args:
            - new_user (User): 새로운 사용자의 정보

        Returns:
            - (User): 등록된 사용자의 정보
        """

        if self.repo.get_user_by_email(new_user.email):
            raise ValueError("User already Exists.")
        
        new_user = self.repo.save_user(new_user)

        return new_user

    def delete_user(self, email: str) -> User:
        """
        이미 등록된 사용자의 정보를 삭제하는 메소드

        Args:
            - email (str): 삭제할 사용자의 email

        Returns:
            - (User): 삭제된 사용자의 정보
        """

        user = self.repo.get_user_by_email(email)
        
        if not user:
            raise ValueError("User not Found.")
        
        deleted_user = self.repo.delete_user(user)

        return deleted_user

    def update_user_pwd(self, user_update: UserUpdate) -> User:
        """
        이미 등록된 사용자의 password를 변경하는 메소드

        Args:
            - user_update (User): password를 변경할 사용자의 정보

        Returns:
            - (User): password가 변경된 사용자의 정보
        """
        
        user = self.repo.get_user_by_email(user_update.email)
        
        if not user:
            raise ValueError("User not Found.")
        
        user.password = user_update.new_password
        updated_user = self.repo.save_user(user)

        return updated_user
        