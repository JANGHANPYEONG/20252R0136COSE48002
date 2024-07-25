//
//
// 처리육 <딥에이징> (ViewModel) : Researcher
// 각 입력 단계를 연결한다.
//
//

import 'package:flutter/widgets.dart';
import 'package:go_router/go_router.dart';
import 'package:structure/main.dart';
import 'package:structure/model/meat_model.dart';
import 'package:structure/components/custom_dialog.dart';

class AddProcessedMeatViewModel with ChangeNotifier {
  bool popup = true;

  /// 처리육 단면 촬영
  void clickedImage(BuildContext context) {
    context.go('/home/data-manage-researcher/add/processed-meat/image');
  }

  /// 처리육 관능평가
  void clickedSensory(BuildContext context) {
    context.go('/home/data-manage-researcher/add/processed-meat/sensory');
  }

  /// 처리육 전자혀 데이터
  void clickedTongue(BuildContext context) {
    context.go('/home/data-manage-researcher/add/processed-meat/tongue');
  }

  /// 처리육 실험 데이터
  void clickedLab(BuildContext context) {
    context.go('/home/data-manage-researcher/add/processed-meat/lab');
  }

  // 가열육 단면 촬영
  void clickedHeatedImage(BuildContext context) {
    context.go('/home/data-manage-researcher/add/processed-meat/heated-image');
  }

  /// 가열육 관능평가
  void clickedHeatedSensory(BuildContext context) {
    context
        .go('/home/data-manage-researcher/add/processed-meat/heated-sensory');
  }

  /// 가열육 전자혀 데이터
  void clickedHeatedTongue(BuildContext context) {
    context.go('/home/data-manage-researcher/add/processed-meat/heated-tongue');
  }

  /// 가열육 실험 데이터
  void clickedHeatedLab(BuildContext context) {
    context.go('/home/data-manage-researcher/add/processed-meat/heated-lab');
  }

  void clickedbutton(BuildContext context, MeatModel model) {
    popup = model.imageCompleted &&
        model.sensoryCompleted &&
        model.tongueCompleted &&
        model.labCompleted &&
        meatModel.heatedImageCompleted &&
        meatModel.heatedSensoryCompleted &&
        meatModel.heatedTongueCompleted &&
        meatModel.heatedLabCompleted;
    if (popup == true) {
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
