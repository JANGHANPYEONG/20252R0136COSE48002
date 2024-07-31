//
//
// 관능 평가 페이지(수정 불가!) : ViewModel
//
//

import 'package:flutter/material.dart';
import 'package:structure/model/meat_model.dart';

class SensoryEvalNotEditableViewModel with ChangeNotifier {
  MeatModel meatModel;
  bool isDeepAged;

  // 초기 데이터 할당
  SensoryEvalNotEditableViewModel(this.meatModel, this.isDeepAged) {
    if (meatModel.sensoryEval != null) {
      meatImage = meatModel.sensoryEval!['imagePath']!;
      marbling = meatModel.sensoryEval!['marbling'];
      color = meatModel.sensoryEval!['color'];
      texture = meatModel.sensoryEval!['texture'];
      surface = meatModel.sensoryEval!['surfaceMoisture'];
      overall = meatModel.sensoryEval!['overall'];
    }
  }

  String meatImage = '';
  double marbling = 1;
  double color = 1;
  double texture = 1;
  double surface = 1;
  double overall = 1;
}
