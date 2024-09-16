//
//
// 원육 추가 정보 입력 (ViewModel) : Researcher
// 각 입력 단계를 연결한다.
//
//

import 'package:flutter/widgets.dart';
import 'package:go_router/go_router.dart';
import 'package:structure/components/custom_dialog.dart';
import 'package:structure/components/custom_pop_up.dart';
import 'package:structure/dataSource/remote_data_source.dart';
import 'package:structure/main.dart';
import 'package:structure/model/meat_model.dart';

class DataAddRawMeatViewModel with ChangeNotifier {
  BuildContext context;

  DataAddRawMeatViewModel({
    required this.context,
  });

  /// 원육 기본정보 (수정 불가)
  void clicekdBasic() {
    context.push('/home/data-manage-researcher/add/raw-meat/info');
  }

  /// 원육 단면 촬영 (수정 불가)
  void clickedBasicImage() {
    context.push('/home/data-manage-researcher/add/raw-meat/image-noteditable');
  }

  /// 원육 관능 평가 (수정 불가)
  void clicekdFresh() {
    context.push('/home/data-manage-researcher/add/raw-meat/sensory');
  }

  /// 원육 전자혀 데이터
  void clickedTongue() {
    context.push('/home/data-manage-researcher/add/raw-meat/tongue');
  }

  /// 원육 실험 데이터
  void clickedLab() {
    context.push('/home/data-manage-researcher/add/raw-meat/lab');
  }

  /// 가열육 관능평가
  void clickedImage() {
    context.push('/home/data-manage-researcher/add/raw-meat/heated-image');
  }

  /// 가열육 전자혀 데이터
  void clickedHeated() {
    context.push('/home/data-manage-researcher/add/raw-meat/heated-sensory');
  }

  /// 가열육 전자혀 데이터
  void clickedHeatedTongue() {
    context.push('/home/data-manage-researcher/add/raw-meat/heated-tongue');
  }

  /// 원육 실험 데이터
  void clickedHeatedLab() {
    context.push('/home/data-manage-researcher/add/raw-meat/heated-lab');
  }

  /// 완료 버튼 클릭
  void clickedbutton(MeatModel model) {
    if (meatModel.tongueCompleted &&
        meatModel.labCompleted &&
        meatModel.heatedImageCompleted &&
        meatModel.heatedSensoryCompleted &&
        meatModel.heatedTongueCompleted &&
        meatModel.heatedLabCompleted) {
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
