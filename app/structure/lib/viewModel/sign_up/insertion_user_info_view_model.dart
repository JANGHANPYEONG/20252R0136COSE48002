import 'package:email_validator/email_validator.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:structure/components/custom_pop_up.dart';
import 'package:structure/main.dart';
import 'package:structure/dataSource/remote_data_source.dart';
import 'package:structure/model/user_model.dart';
import 'package:structure/config/labels.dart';

class InsertionUserInfoViewModel with ChangeNotifier {
  InsertionUserInfoViewModel(UserModel userModel) {
    initialize();
  }

  // form
  final formKey = GlobalKey<FormState>();

  TextEditingController name = TextEditingController();
  TextEditingController email = TextEditingController();
  TextEditingController password = TextEditingController();
  TextEditingController cPassword = TextEditingController();

  void initialize() {
    userModel.reset();
  }

  bool isUnique = false;

  // 버튼 활성화 확인을 위한 변수
  bool isValidId = false;
  bool isValidPw = false;
  bool isValidCPw = false;

  // 약관 동의 확인을 위한 변수
  bool isChecked1 = false;
  bool isChecked2 = false;
  bool isChecked3 = false;
  bool isChecked4 = false;
  bool isRequiredChecked = false;

  //이메일 중복 확인 로딩 여부 확인 변수
  bool emailCheckLoading = false;

  /// 아이디 유효성 검사
  String? idValidate(String? value) {
    // 비어있지 않고 이메일 형식에 맞지 않을 때, 빨간 예외 메시지
    final bool isValid = EmailValidator.validate(value!);
    if (value.isNotEmpty && !isValid) {
      isValidId = false;
      return '이메일 형식이 올바르지 않습니다.';
    } else if (value.isEmpty) {
      isValidId = false;
      return null;
    } else {
      isValidId = true;
      return null;
    }
  }

  // 비밀번호 유효성 검사
  String? pwValidate(String? value) {
    // 비어있지 않고 비밀번호 형식에 맞지 않을 때, 빨간 에러 메시지
    final bool isValid = validatePassword(value!);
    if (value.isNotEmpty && !isValid) {
      isValidPw = false;
      return Labels.pwdErrorStr;
    } else if (value.isEmpty) {
      isValidPw = false;
      return null;
    } else {
      isValidPw = true;
      return null;
    }
  }

  // 비밀번호 재입력 유효성 검사
  String? cPwValidate(String? value) {
    // 비어있지 않고 비밀번호와 같지 않을 때, 빨간 에러 메시지
    if (value!.isNotEmpty && value != password.text) {
      isValidCPw = false;
      return Labels.pwdNotSame;
    } else if (value.isEmpty) {
      isValidCPw = false;
      return null;
    } else {
      isValidCPw = true;
      return null;
    }
  }

  void onChangeEmail(String? v) {
    isUnique = false;
    notifyListeners();
  }

  // 유효성 검사 함수
  void tryValidation() {
    final isValid = formKey.currentState!.validate();
    if (isValid) {
      formKey.currentState!.save();
    }
    notifyListeners();
  }

  // 비밀번호 유효성 검사 (정규식)
  bool validatePassword(String password) {
    // 조건: 영문 대/소문자, 숫자, 특수문자 10자~15자
    const pattern =
        r'^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[!@#$%^&*()\-_=+{};:,<.>]).{10,15}$';
    final regex = RegExp(pattern);

    return regex.hasMatch(password);
  }

  // 이메일 중복 검사
  Future<void> dupliCheck(BuildContext context) async {
    //이메일 중복 검사 로딩중인 상태
    emailCheckLoading = true;
    notifyListeners();

    dynamic isDuplicated = await RemoteDataSource.dupliCheck(email.text);

    if (isDuplicated != null) {
      isUnique = true;
      emailCheckLoading = false;
      notifyListeners();
    } else {
      isUnique = false;
      emailCheckLoading = false;
      notifyListeners();

      // popup 창 띄우기
      if (context.mounted) showDuplicateEmailPopup(context);
    }
  }

  // 필수 동의 체크 확인
  void _checkCheckBoxValues() {
    if (isChecked2 == true && isChecked3 == true && isChecked4 == true) {
      isChecked1 = true;
    } else {
      isChecked1 = false;
    }
    if (isChecked2 == true && isChecked3 == true) {
      isRequiredChecked = true;
    } else {
      isRequiredChecked = false;
    }
    notifyListeners();
  }

  // 첫 번째 체크박스 클릭 시
  void clicked1stCheckBox(bool? value) {
    isChecked1 = value!;
    isChecked2 = value;
    isChecked3 = value;
    isChecked4 = value;
    _checkCheckBoxValues();
  }

  // 두 번째 체크박스 클릭 시
  void clicked2ndCheckBox(bool? value) {
    isChecked2 = value!;
    _checkCheckBoxValues();
  }

  // 세 번째 체크박스 클릭 시
  void clicked3rdCheckBox(bool? value) {
    isChecked3 = value!;
    _checkCheckBoxValues();
  }

  // 모두 동의 클릭 시
  void clicked4thCheckBox(bool? value) {
    isChecked4 = value!;
    _checkCheckBoxValues();
  }

  // 모든 값이 올바르게 입력됐는지 확인
  bool isAllChecked() {
    if (isValidId &&
        isValidPw &&
        isValidCPw &&
        isUnique &&
        name.text.isNotEmpty &&
        isRequiredChecked) {
      return true;
    }
    return false;
  }

  void saveUserInfo() {
    userModel.userId = email.text;
    userModel.password = password.text;
    userModel.name = name.text;
    userModel.alarm = isChecked4;
  }

  void clickedNextButton(BuildContext context) {
    saveUserInfo();
    context.go('/sign-in/sign-up/user-detail');
  }
}
