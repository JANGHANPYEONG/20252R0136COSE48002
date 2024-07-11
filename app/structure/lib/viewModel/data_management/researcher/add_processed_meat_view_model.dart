//
//
// 처리육 <딥에이징> (ViewModel) : Researcher
// 각 입력 단계를 연결한다.
//
//

import 'package:flutter/widgets.dart';
import 'package:go_router/go_router.dart';

class AddProcessedMeatViewModel with ChangeNotifier {
  AddProcessedMeatViewModel();

  /// 사진 촬영 페이지로 이동
  void clickedImage(BuildContext context) {
    context.go('/home/data-manage-researcher/add/processed-meat/image');
  }

  /// 관능평가 페이지로 이동
  void clickedEval(BuildContext context) {
    context.go('/home/data-manage-researcher/add/processed-meat/eval');
  }

  /// 관능평가 페이지로 이동
  void clickedHeatedEval(BuildContext context) {
    context.go('/home/data-manage-researcher/add/processed-meat/heated-eval');
  }

  /// 전자혀 페이지로 이동
  void clickedTongue(BuildContext context) {
    context.go('/home/data-manage-researcher/add/processed-meat/tongue');
  }

  /// 실험실 데이터 페이지로 이동
  void clickedLab(BuildContext context) {
    context.go('/home/data-manage-researcher/add/processed-meat/lab');
  }
}
