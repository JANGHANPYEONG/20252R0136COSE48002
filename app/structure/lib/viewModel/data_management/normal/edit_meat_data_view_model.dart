//
//
// 데이터 수정(열람) 페이지 (ViewModel) : Normal
//
//

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:structure/config/userfuls.dart';
import 'package:structure/model/meat_model.dart';

class EditMeatDataViewModel with ChangeNotifier {
  MeatModel meatModel;
  EditMeatDataViewModel(this.meatModel) {
    // 만약 데이터의 상태가 '대기중'이며, 3일 내 등록 데이터이면 수정 가능으로 만든다.
    if (meatModel.statusType == '대기중' &&
        Usefuls.calculateDateDifference(meatModel.createdAt!) <= 3) {
      isEditable = true;
    }
  }

  bool isEditable = false;

  void clicekdBasic(BuildContext context) {
    if (isEditable) {
      context.go('/home/data-manage-normal/edit/trace-editable');
    } else {
      context.go('/home/data-manage-normal/edit/trace');
    }
  }

  void clickedImage(BuildContext context) {
    if (isEditable) {
      context.go('/home/data-manage-normal/edit/image-editable');
    } else {
      context.go('/home/data-manage-normal/edit/image');
    }
  }

  void clicekdFresh(BuildContext context) {
    if (isEditable) {
      context.go('/home/data-manage-normal/edit/freshmeat-editable');
    } else {
      context.go('/home/data-manage-normal/edit/freshmeat');
    }
  }
}
