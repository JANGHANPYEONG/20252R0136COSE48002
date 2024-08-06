import 'package:email_validator/email_validator.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:structure/components/custom_pop_up.dart';
import 'package:structure/main.dart';
import 'package:structure/dataSource/remote_data_source.dart';
import 'package:structure/model/user_model.dart';
import 'package:structure/config/labels.dart';
import 'package:structure/components/custom_dialog.dart';

class InsertionUserInfoViewModel with ChangeNotifier {
  InsertionUserInfoViewModel(UserModel userModel) {
    userModel.reset();
  }

  bool isDupActivateButton = false; // 중복확인 버튼 활성화

  // form
  final formKey = GlobalKey<FormState>();

  TextEditingController name = TextEditingController();
  TextEditingController email = TextEditingController();
  TextEditingController password = TextEditingController();
  TextEditingController cPassword = TextEditingController();

  bool isUnique = false;

  // 버튼 활성화 확인을 위한 변수
  bool isValidId = false;
  bool isValidPw = false;
  bool isValidCPw = false;
  bool isName = false;

  // 약관 동의 확인을 위한 변수
  bool isChecked1 = false;
  bool isChecked2 = false;
  bool isChecked3 = false;
  bool isChecked4 = false;
  bool isRequiredChecked = false;

  // 이메일 중복 확인 로딩 여부 확인 변수
  bool emailCheckLoading = false;

  late BuildContext _context;

  /// 이름 입력 여부 검사
  void nameCheck(String? value) {
    isName = true;
    notifyListeners();
  }

  /// 아이디 유효성 검사
  /// 비어있지 않고 이메일 형식에 맞지 않을 때, 빨간 예외 메시지를 띄움
  String? idValidate(String? value) {
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

  void onChangeEmail(String? value) {
    isUnique = false; // 이메일 입력된 값이 바뀌면 isUnique는 다시 false로 세팅
    notifyListeners();
    final bool isValid = EmailValidator.validate(value!);
    if (value.isNotEmpty && !isValid) {
      isValidId = false;
    } else if (value.isEmpty) {
      isValidId = false;
    } else {
      isValidId = true;
    }
  }

  /// 비밀번호 유효성 검사
  /// 비어있지 않고 비밀번호 형식에 맞지 않을 때, 빨간 에러 메시지를 띄움
  String? pwValidate(String? value) {
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

  /// 비밀번호 재입력 유효성 검사
  /// 비어있지 않고 비밀번호와 같지 않을 때, 빨간 에러 메시지를 띄움
  String? cPwValidate(String? value) {
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

  /// 비밀번호 유효성 검사 (정규식)
  /// 조건: 영문 대/소문자, 숫자, 특수문자 10자 이상
  bool validatePassword(String password) {
    const pattern = Labels.pwdPattern;
    final regex = RegExp(pattern);

    return regex.hasMatch(password);
  }

  /// 이메일 중복 검사
  Future<void> dupliCheck(BuildContext context) async {
    // 이메일 중복 검사 로딩중인 상태
    emailCheckLoading = true;
    notifyListeners();

    // 중복 확인
    dynamic response = await RemoteDataSource.dupliCheck(email.text);

    // response 값 확인
    if (response is Map<String, dynamic>) {
      // 200 OK
      isUnique = !response['isDuplicated'];
      emailCheckLoading = false;
      notifyListeners();

      //이메일 중복인 경우
      if (!isUnique) {
        // 중복 popup 창 띄우기
        _context = context;
        if (context.mounted) {
          showDuplicateIdSigninDialog(context, context.pop, moveSignIn);
        }
      }
    } else {
      // 오류
      isUnique = false;
      emailCheckLoading = false;
      notifyListeners();

      if (context.mounted) showErrorPopup(context);
    }
  }

  /// popup 확인
  void moveSignIn() {
    _context.go('/sign-in');
  }

  /// 필수 동의 체크 확인
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

  /// 첫 번째 체크박스 클릭 시
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
    userModel.userId = email.text.trim();
    userModel.name = name.text.trim();
    userModel.type = 'Normal';
    userModel.alarm = isChecked4;
    userModel.password = password.text.trim();
  }

  void clickedNextButton(BuildContext context) {
    saveUserInfo();
    context.go('/sign-in/sign-up/user-detail');
  }
}
