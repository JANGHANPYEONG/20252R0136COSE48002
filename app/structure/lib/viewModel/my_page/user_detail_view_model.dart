import 'package:flutter/material.dart';
import 'package:kpostal/kpostal.dart';
import 'package:structure/components/custom_app_bar.dart';
import 'package:structure/components/custom_pop_up.dart';
import 'package:structure/dataSource/remote_data_source.dart';
import 'package:structure/model/user_model.dart';

class UserDetailViewModel with ChangeNotifier {
  UserModel userModel;
  UserDetailViewModel(this.userModel) {
    _initialize();
  }
  bool isLoading = false;

  String userId = '';
  bool isEditting = false;
  bool isActivateButton = false;
  bool isChecked = false; // 약관 동의 여부

  final TextEditingController mainAddress = TextEditingController();
  final TextEditingController subAddress = TextEditingController();
  final TextEditingController company = TextEditingController();
  final TextEditingController department = TextEditingController();
  final TextEditingController jobTitle = TextEditingController();

  void onChangedSubAdress(String value) {
    isActivateButton = true;
    notifyListeners();
  }

  void onChangedCompany(String value) {
    isActivateButton = true;
    notifyListeners();
  }

  void onChangedDepartment(String value) {
    isActivateButton = true;
    notifyListeners();
  }

  void onChangedJobTitle(String value) {
    isActivateButton = true;
    notifyListeners();
  }

  /// 주소 검색 버튼 클릭
  Future<void> clickedSearchButton(BuildContext context) async {
    isActivateButton = true;
    await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => KpostalView(
          appBar: const CustomAppBar(
              title: '주소검색', backButton: true, closeButton: false),
          useLocalServer: false,
          callback: (Kpostal result) {
            mainAddress.text = result.jibunAddress;
            subAddress.text = '';
            notifyListeners();
          },
        ),
      ),
    );
  }

  // TODO
  void clicked1stCheckBox(bool? value) {
    // isChecked = ;
  }

  Future<void> clickedSaveButton(BuildContext context) async {
    isLoading = true;
    isActivateButton = false;
    notifyListeners();

    if (mainAddress.text.isNotEmpty) {
      userModel.homeAdress = '${mainAddress.text}/${subAddress.text}';
    }

    userModel.company = company.text;
    if (department.text.isNotEmpty || jobTitle.text.isNotEmpty) {
      userModel.jobTitle = '${department.text}/${jobTitle.text}';
    }

    try {
      // 데이터 전송
      final response = await RemoteDataSource.updateUser(userModel.toJson());
      if (response == 200) {
        if (context.mounted) showSuccessChangeUserInfo(context);
      } else {
        throw Error();
      }
    } catch (e) {
      debugPrint('$e');
      if (context.mounted) showErrorPopup(context);
    }

    isLoading = false;
    notifyListeners();
  }

  void _initialize() {
    userId = userModel.userId ?? 'None';
    if (userModel.alarm != null) {
      isChecked = userModel.alarm!;
      print('');
    }
    // isChecked =
    print('체크 : $isChecked');
    if (userModel.homeAdress != null && userModel.homeAdress!.isNotEmpty) {
      int index = userModel.homeAdress!.indexOf('/');
      if (index != -1 && userModel.homeAdress!.substring(0, index).isNotEmpty) {
        mainAddress.text = userModel.homeAdress!.substring(0, index);
      }
      if (index != -1 &&
          userModel.homeAdress!.substring(index + 1).isNotEmpty) {
        subAddress.text = userModel.homeAdress!.substring(index + 1);
      }
    }
    if (userModel.company != null && userModel.company!.isNotEmpty) {
      company.text = userModel.company!;
    }
    if (userModel.jobTitle != null && userModel.jobTitle!.isNotEmpty) {
      int index = userModel.jobTitle!.indexOf('/');
      if (index != -1 && userModel.jobTitle!.substring(0, index).isNotEmpty) {
        department.text = userModel.jobTitle!.substring(0, index);
      }
      if (index != -1 && userModel.jobTitle!.substring(index + 1).isNotEmpty) {
        jobTitle.text = userModel.jobTitle!.substring(index + 1);
      }
    }
  }
}
