//
//
// 처리육 <딥에이징> (ViewModel) : Researcher
// 각 입력 단계를 연결한다.
//
//

import 'package:flutter/widgets.dart';
import 'package:go_router/go_router.dart';
import 'package:structure/components/custom_pop_up.dart';
import 'package:structure/dataSource/remote_data_source.dart';
import 'package:structure/main.dart';
import 'package:structure/model/meat_model.dart';
import 'package:structure/components/custom_dialog.dart';

class DataAddProcessedMeatViewModel with ChangeNotifier {
  bool popup = true;
  BuildContext context;

  DataAddProcessedMeatViewModel({
    required this.context,
  });

  /// 처리육 단면 촬영
  void clickedImage() {
    context.push('/home/data-manage-researcher/add/processed-meat/image');
  }

  /// 처리육 관능평가
  void clickedSensory() {
    context.push('/home/data-manage-researcher/add/processed-meat/sensory');
  }

  /// 처리육 전자혀 데이터
  void clickedTongue() {
    context.push('/home/data-manage-researcher/add/processed-meat/tongue');
  }

  /// 처리육 실험 데이터
  void clickedLab() {
    context.push('/home/data-manage-researcher/add/processed-meat/lab');
  }

  // 가열육 단면 촬영
  void clickedHeatedImage() {
    context
        .push('/home/data-manage-researcher/add/processed-meat/heated-image');
  }

  /// 가열육 관능평가
  void clickedHeatedSensory() {
    context
        .push('/home/data-manage-researcher/add/processed-meat/heated-sensory');
  }

  /// 가열육 전자혀 데이터
  void clickedHeatedTongue() {
    context
        .push('/home/data-manage-researcher/add/processed-meat/heated-tongue');
  }

  /// 가열육 실험 데이터
  void clickedHeatedLab() {
    context.push('/home/data-manage-researcher/add/processed-meat/heated-lab');
  }

  void clickedbutton(MeatModel model) {
    popup = model.imageCompleted &&
        model.sensoryCompleted &&
        model.tongueCompleted &&
        model.labCompleted &&
        meatModel.heatedImageCompleted &&
        meatModel.heatedSensoryCompleted &&
        meatModel.heatedTongueCompleted &&
        meatModel.heatedLabCompleted;
    if (popup == true) {
      showDataCompleteDialog(context, () async {
        await deepAgingComplete(context);
      });
    } else {
      showDataNotCompleteDialog(context, () async {
        await deepAgingComplete(context);
      });
    }
  }

  Future<void> deepAgingComplete(BuildContext context) async {
    try {
      meatModel.isCompleted = 2;

      // 완료 상태로 변경
      final response = await RemoteDataSource.patchMeatData(
          'deep-aging-data', meatModel.toJsonDeepAging());
      if (response == 200) {
        meatModel.updateIsCompleted();
        if (context.mounted) {
          context.pop();
          context.pop();
        }
      } else {
        throw ErrorDescription(response);
      }
    } catch (e) {
      debugPrint('Error: $e');
      if (context.mounted) context.pop();
      if (context.mounted) showErrorPopup(context, error: e.toString());
    }
  }
}
