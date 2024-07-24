//
//
// 원육 추가 정보 입력 (ViewModel) : Researcher
// 각 입력 단계를 연결한다.
//
//

import 'package:flutter/widgets.dart';
import 'package:go_router/go_router.dart';
import 'package:structure/components/custom_dialog.dart';
import 'package:structure/main.dart';
import 'package:structure/model/meat_model.dart';

class AddRawMeatViewModel with ChangeNotifier {
  /// 원육 기본정보 (수정 불가)
  void clicekdBasic(BuildContext context) {
    context.go('/home/data-manage-researcher/add/raw-meat/info');
  }

  /// 원육 단면 촬영 (수정 불가)
  void clickedBasicImage(BuildContext context) {
    context.go('/home/data-manage-researcher/add/raw-meat/image-noteditable');
  }

  /// 원육 관능 평가 (수정 불가)
  void clicekdFresh(BuildContext context) {
    context.go('/home/data-manage-researcher/add/raw-meat/sensory');
  }

  /// 원육 전자혀 데이터
  void clickedTongue(BuildContext context) {
    context.go('/home/data-manage-researcher/add/raw-meat/tongue');
  }

  /// 원육 실험 데이터
  void clickedLab(BuildContext context) {
    context.go('/home/data-manage-researcher/add/raw-meat/lab');
  }

  /// 가열육 관능평가
  void clickedImage(BuildContext context) {
    context.go('/home/data-manage-researcher/add/raw-meat/heated-image');
  }

  /// 가열육 전자혀 데이터
  void clickedHeated(BuildContext context) {
    context.go('/home/data-manage-researcher/add/raw-meat/heated-sensory');
  }

  /// 가열육 전자혀 데이터
  void clickedHeatedTongue(BuildContext context) {
    context.go('/home/data-manage-researcher/add/raw-meat/heated-tongue');
  }

  /// 원육 실험 데이터
  void clickedHeatedLab(BuildContext context) {
    context.go('/home/data-manage-researcher/add/raw-meat/heated-lab');
  }

  /// 완료 버튼 클릭
  void clickedbutton(BuildContext context, MeatModel model) {
    // popup = model.deepAgedImageCompleted &&
    //     model.deepAgedFreshCompleted &&
    //     model.heatedCompleted &&
    //     model.tongueCompleted &&
    //     model.labCompleted;

    if (meatModel.heatedCompleted &&
        meatModel.labCompleted &&
        meatModel.tongueCompleted) {
      showDataCompleteDialog(context, null, () {
        context.go('/home/data-manage-researcher/add');
      });
    } else {
      showDataNotCompleteDialog(context, null, () {
        context.go('/home/data-manage-researcher/add');
      });
    }
  }
}
