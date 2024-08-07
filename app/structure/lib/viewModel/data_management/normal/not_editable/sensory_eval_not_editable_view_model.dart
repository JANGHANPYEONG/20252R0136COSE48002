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

      dataText = marbling.toString();
    }
  }

  List<List<String>> text = [
    ['Mabling', '마블링 정도', '없음', '', '보통', '', '많음'],
    ['Color', '육색', '없음', '', '보통', '', '어둡고 진함'],
    ['Texture', '조직감', '물렁함', '', '보통', '', '단단함'],
    ['Surface Moisture', '표면육즙', '적음', '', '보통', '', '많음'],
    ['Overall', '종합기호도', '나쁨', '', '보통', '', '좋음'],
  ];

  // Sensory 데이터
  String meatImage = '';
  double marbling = 1;
  double color = 1;
  double texture = 1;
  double surface = 1;
  double overall = 1;

  // 데이터 텍스트
  String dataText = '';

  void updateDataText(int idx) {
    switch (idx) {
      case 0:
        dataText = marbling.toString();
        break;
      case 1:
        dataText = color.toString();
        break;
      case 2:
        dataText = texture.toString();
        break;
      case 3:
        dataText = surface.toString();
        break;
      case 4:
        dataText = overall.toString();
        break;
      default:
        dataText = '';
        break;
    }

    notifyListeners();
  }
}
