import 'package:flutter/material.dart';
import 'package:structure/model/meat_model.dart';
import 'package:structure/model/user_model.dart';

class DataManagementHomeTabViewModel with ChangeNotifier {
  MeatModel meatModel;
  UserModel userModel;
  DataManagementHomeTabViewModel(this.meatModel, this.userModel);
}
