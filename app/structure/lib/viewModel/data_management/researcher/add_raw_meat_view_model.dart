//
//
// 원육 (ViewModel) : Researcher
// 각 입력 단계를 연결한다.
//
//

import 'package:flutter/widgets.dart';
import 'package:go_router/go_router.dart';
import 'package:structure/components/custom_dialog.dart';
import 'package:structure/main.dart';
import 'package:structure/model/meat_model.dart';

class AddRawMeatViewModel with ChangeNotifier {
  bool popup = true;
  void clickedHeated(BuildContext context) {
    context.go('/home/data-manage-researcher/add/raw-meat/heated-meat');
  }

  void clickedTongue(BuildContext context) {
    context.go('/home/data-manage-researcher/add/raw-meat/tongue');
  }

  void clickedLab(BuildContext context) {
    context.go('/home/data-manage-researcher/add/raw-meat/lab');
  }

  void clickedImage(BuildContext context) {
    //바꿔야함
    context.go('/home/data-manage-researcher/add/raw-meat/image');
  }

  bool isEditable = false;
  bool isNormal = true;

  void clicekdBasic(BuildContext context) {
    context.go('/home/data-manage-researcher/add/raw-meat/info');
  }

  void clickedBasicImage(BuildContext context) {
    context.go('/home/data-manage-researcher/add/raw-meat/image-noteditable');
  }

  void clicekdFresh(BuildContext context) {
    context.go('/home/data-manage-researcher/add/raw-meat/freshmeat');
  }

  void clickedbutton(BuildContext context, MeatModel model) {
    // popup = model.deepAgedImageCompleted &&
    //     model.deepAgedFreshCompleted &&
    //     model.heatedCompleted &&
    //     model.tongueCompleted &&
    //     model.labCompleted;
    popup = meatModel.heatedCompleted &&
        meatModel.labCompleted &&
        meatModel.tongueCompleted;

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
