import 'package:flutter/widgets.dart';
import 'package:go_router/go_router.dart';
import 'package:structure/components/custom_pop_up.dart';
import 'package:structure/model/user_model.dart';

class HomeViewModel with ChangeNotifier {
  UserModel userModel;

  String userType = '';

  HomeViewModel({required this.userModel}) {
    _initialize();
  }
  void _initialize() {
    if (userModel.type != null) {
      if (userModel.type == 'Normal') {
        userType = 'Normal';
      } else if (userModel.type == 'Researcher') {
        userType = 'Researcher';
      } else if (userModel.type == 'Manager') {
        userType = 'Manager';
      } else {
        userType = 'None';
      }
    }
    print('타입 : ${userModel.type}');
    print('타입 : $userType');
  }

  void clickedMyPage(BuildContext context) {
    context.go('/home/my-page');
  }

  void clickedMeatRegist(BuildContext context) {
    context.go('/home/registration');
  }

  void clickedDataManage(BuildContext context) {
    if (userModel.type == 'Normal') {
      context.go('/home/data-manage-normal');
    } else if (userModel.type == 'Researcher' || userModel.type == 'Manager') {
      context.go('/home/data-manage-researcher');
    } else {
      showUserTypeErrorPopup(context);
    }
  }
}
