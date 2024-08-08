//
//
// 육류 이미지 페이지(수정 불가!) : ViewModel
//
//

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:structure/config/usefuls.dart';
import 'package:structure/model/meat_model.dart';

class InsertionMeatImageNotEditableViewModel with ChangeNotifier {
  final MeatModel meatModel;

  InsertionMeatImageNotEditableViewModel(this.meatModel) {
    if (meatModel.sensoryEval != null) {
      imagePath = meatModel.sensoryEval!['imagePath'];
      date = Usefuls.parseDate(meatModel.sensoryEval!['filmedAt']);
      userName = meatModel.sensoryEval!['userName'];
    }
  }
  String date = '-';
  String userName = '-';
  String? imagePath;

  void clickedNextButton(BuildContext context) {
    context.go('/home/data-manage-normal/edit');
  }
}
