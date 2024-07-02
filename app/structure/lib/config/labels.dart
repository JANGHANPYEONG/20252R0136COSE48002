class Labels {
  //비밀번호
  static const pwdErrorStr = "대소문자, 숫자, 특수문자를 포함해 10자 이상으로 입력하세요.";
  static const pwdPattern =
      r'^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[!@#$%^&*()\-_=+{};:,<.>]).{10,}$';
  static const pwdNotSame = "비밀번호가 일치하지 않습니다.";
}
