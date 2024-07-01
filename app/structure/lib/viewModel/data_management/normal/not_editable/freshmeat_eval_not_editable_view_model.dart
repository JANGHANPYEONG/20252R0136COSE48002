//
//
// 관능 평가 페이지(수정 불가!) : ViewModel
//
//

import 'package:flutter/material.dart';
import 'package:structure/model/meat_model.dart';

class FreshMeatEvalNotEditableViewModel with ChangeNotifier {
  MeatModel meatModel;
  bool isDeepAged;

  // 초기 데이터 할당
  FreshMeatEvalNotEditableViewModel(this.meatModel, this.isDeepAged) {
    meatImage = meatModel.imagePath!;
    marbling = meatModel.freshmeat!["marbling"];
    color = meatModel.freshmeat!["color"];
    texture = meatModel.freshmeat!['texture'];
    surface = meatModel.freshmeat!['surfaceMoisture'];
    overall = meatModel.freshmeat!['overall'];
  }

  String meatImage = '';

  double marbling = 0;
  double color = 0;
  double texture = 0;
  double surface = 0;
  double overall = 0;
}
