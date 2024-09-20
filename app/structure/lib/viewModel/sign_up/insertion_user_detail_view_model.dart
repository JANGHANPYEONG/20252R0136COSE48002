import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:kpostal/kpostal.dart';
import 'package:structure/components/custom_app_bar.dart';
import 'package:structure/components/custom_pop_up.dart';
import 'package:structure/dataSource/local_data_source.dart';
import 'package:structure/dataSource/remote_data_source.dart';
import 'package:structure/model/user_model.dart';

class InsertionUserDetailViewModel with ChangeNotifier {
  UserModel userModel;
  BuildContext context;
  InsertionUserDetailViewModel({
    required this.userModel,
    required this.context,
  });

  bool isLoading = false;
  bool emailcheck = false;

  final TextEditingController mainAddressController = TextEditingController();

  String subHomeAdress = '';
  String company = '';
  String department = '';
  String jobTitle = '';

  /// 검색 버튼 클릭
  Future clickedSearchButton() async {
    await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => KpostalView(
          useLocalServer: false,
          callback: (Kpostal result) {
            mainAddressController.text = result.jibunAddress;
            notifyListeners();
          },
          appBar: const CustomAppBar(title: '주소검색'),
        ),
      ),
    );
  }

  /// 다음 버튼 클릭시
  Future<void> clickedNextButton() async {
    isLoading = true;
    notifyListeners();

    try {
      _saveUserData();
      await _sendData();

      await LocalDataSource.deleteLocalData(userModel.userId!);
    } catch (e) {
      debugPrint('Error: $e');
      if (context.mounted) showErrorPopup(context, error: e.toString());
    }

    isLoading = false;
    notifyListeners();
  }

  void _saveUserData() {
    if (mainAddressController.text.isNotEmpty) {
      userModel.homeAdress = '${mainAddressController.text}/$subHomeAdress';
    }

    userModel.company = company;
    if (department.isNotEmpty || jobTitle.isNotEmpty) {
      userModel.jobTitle = '$department/$jobTitle';
    }
  }

  /// 데이터 서버로 전송
  Future<void> _sendData() async {
    FirebaseAuth firebaseAuth = FirebaseAuth.instance;

    try {
      // 사용자의 회원가입 정보를 서버로 전송
      dynamic response = await RemoteDataSource.signUp(userModel.toJson());
      if (response == 200) {
        // 새로운 유저 생성
        UserCredential credential =
            await firebaseAuth.createUserWithEmailAndPassword(
          email: userModel.userId!,
          password: userModel.password!,
        );

        // 이메일 인증 메일 전송
        if (credential.user != null) {
          await credential.user!.sendEmailVerification();
          emailcheck = true;
        } else {
          throw ErrorDescription('User does not exist');
        }

        userModel.password = null; // 계정 생성 완료 후 userModel에서 비밀번호 초기화
        if (context.mounted) context.go('/sign-in/complete-sign-up');
      } else {
        throw ErrorDescription(response);
      }
    } on FirebaseAuthException catch (e) {
      switch (e.code) {
        case 'email-already-in-use':
          debugPrint('이메일 중복');
          break;
        case 'invalid-email':
          debugPrint('올바르지 않은 이메일');
          break;
        default:
          debugPrint('Error: ${e.code}');
          break;
      }

      if (context.mounted) showErrorPopup(context, error: e.code);
    } catch (e) {
      debugPrint('Error: $e');
      if (context.mounted) showErrorPopup(context, error: e.toString());
    }
  }
}
