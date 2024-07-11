//
//
// 원육 (ViewModel) : Researcher
// 각 입력 단계를 연결한다.
//
//

import 'package:flutter/widgets.dart';
import 'package:go_router/go_router.dart';

class AddRawMeatViewModel with ChangeNotifier {
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
    if (isNormal) {
      if (isEditable) {
        context.go('/home/data-manage-normal/edit/info-editable');
      } else {
        context.go('/home/data-manage-normal/edit/info');
      }
    } else {
      context.go('/home/data-manage-researcher/approve/info');
    }
  }

  void clickedBasicImage(BuildContext context) {
    if (isNormal) {
      if (isEditable) {
        context.go('/home/data-manage-normal/edit/image-editable');
      } else {
        context.go('/home/data-manage-normal/edit/image');
      }
    } else {
      context.go('/home/data-manage-researcher/approve/image');
    }
  }

  void clicekdFresh(BuildContext context) {
    if (isNormal) {
      if (isEditable) {
        context.go('/home/data-manage-normal/edit/freshmeat-editable');
      } else {
        context.go('/home/data-manage-normal/edit/freshmeat');
      }
    } else {
      context.go('/home/data-manage-researcher/approve/freshmeat');
    }
  }
}
