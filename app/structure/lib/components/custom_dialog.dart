import 'dart:io';

import 'package:structure/config/pallete.dart';
import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';

/// 사진 삭제 dialog
void showDeletePhotoDialog(BuildContext context, VoidCallback? rightFunc) {
  showCustomDialog(
    context,
    'assets/images/trash_image.png',
    '사진을 삭제할까요?',
    '삭제된 사진은 복구할 수 없습니다.',
    '취소',
    '삭제',
    null,
    rightFunc,
  );
}

/// 나가기 dialog
void showExitDialog(BuildContext context) {
  showCustomDialog(context, 'assets/images/exit.png', '데이터가 저장되지 않았습니다',
      '창을 닫으면 모든 정보가 삭제됩니다.', '취소', '나가기', null, () {
    FocusScope.of(context).unfocus();
    Navigator.pop(context);
    Navigator.pop(context);
  });
}

/// 임시저장 불러오기 dialog
void showDataRegisterDialog(
    BuildContext context, VoidCallback? leftFunc, VoidCallback? rightFunc) {
  showCustomDialog(
    context,
    'assets/images/temporarySave.png',
    '임시저장 중인 데이터가 있습니다.',
    '이어서 등록하시겠습니까?',
    '처음부터 등록하기',
    '이어서 등록하기',
    leftFunc,
    rightFunc,
  );
}

/// 데이터 입력 미완료 dialog
void showDataNotCompleteDialog(
    BuildContext context, VoidCallback? leftFunc, VoidCallback? rightFunc) {
  showCustomDialog(
    context,
    null,
    '아직 입력되지 않은 정보가 있습니다.',
    '저장하시겠습니까?',
    '취소',
    '확인',
    null,
    rightFunc,
  );
}

/// 데이터 입력 완료 dialog
void showDataCompleteDialog(
    BuildContext context, VoidCallback? leftFunc, VoidCallback? rightFunc) {
  showCustomDialog(
    context,
    null,
    '완료하시겠습니까?',
    '',
    '취소',
    '확인',
    null,
    rightFunc,
  );
}

/// 중복 이메일 dialog
void showDuplicateIdSigninDialog(
    BuildContext context, VoidCallback? leftFunc, VoidCallback? rightFunc) {
  showCustomDialog(
    context,
    null,
    '중복된 이메일입니다.',
    '기존 계정으로 로그인 해주세요.',
    '취소',
    '로그인',
    null,
    rightFunc,
  );
}

/// 회원 탈퇴 dialog
void showDeleteIdDialog(
    BuildContext context, VoidCallback? leftFunc, VoidCallback? rightFunc) {
  showCustomDialog(
    context,
    null,
    '회원탈퇴를 진행하시겠습니까?',
    '탈퇴 완료 이후에는 되돌릴 수 없습니다.',
    '취소',
    '탈퇴',
    leftFunc,
    rightFunc,
  );
}

/// 임시저장 dialog
void showTemporarySaveDialog(BuildContext context, VoidCallback? rightFunc) {
  showCustomDialog(
    context,
    'assets/images/exit.png',
    '임시저장 하시겠습니까?',
    '',
    '아니요',
    '네',
    null,
    rightFunc,
  );
}

/// 딥에이징 데이터 삭제 dialog
void showDeepAgingDeleteDialog(BuildContext context, VoidCallback? rightFunc) {
  void handleRightFunc() {
    if (rightFunc != null) {
      rightFunc();
    }
    Navigator.of(context).pop();
  }

  showCustomDialog(
    context,
    'assets/images/trash_image.png',
    '딥에이징 정보를 삭제할까요?',
    '관련된 모든 데이터가 삭제됩니다. \n 삭제한 데이터는 되돌릴 수 없습니다.',
    '취소',
    '삭제',
    null,
    handleRightFunc,
  );
}

// 다이얼로그 형식입니다.
/// 커스텀 dialog
void showCustomDialog(
  BuildContext context,
  String? iconPath,
  String titleText,
  String contentText,
  String leftButtonText,
  String rightButtonText,
  VoidCallback? leftButtonFunc,
  VoidCallback? rightButtonFunc,
) {
  showDialog(
    context: context,
    barrierDismissible: false,
    builder: (BuildContext context) {
      return Dialog(
        insetPadding: EdgeInsets.all(30.w),
        backgroundColor: Colors.white,
        shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.all(Radius.circular(20.r))),
        child: SizedBox(
          height: iconPath != null ? 504.h : 332.h,
          width: 650.w,
          child: Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                iconPath != null
                    ? SizedBox(
                        height: 140.h,
                        width: 140.w,
                        child: Image.asset(
                          iconPath,
                        ),
                      )
                    : Container(),
                SizedBox(height: 25.h),
                Text(
                  titleText,
                  style: Palette.dialogContentBold,
                  textAlign: TextAlign.center,
                ),
                SizedBox(height: 14.h),
                Text(
                  contentText,
                  textAlign: TextAlign.center,
                  style: Palette.dialogContentSmall,
                ),
                iconPath != null
                    ? SizedBox(height: 74.h)
                    : SizedBox(height: 50.h),
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    // 왼쪽 버튼
                    DialogButton(
                      buttonFunc: leftButtonFunc ??
                          () {
                            Navigator.pop(context);
                          },
                      buttonText: leftButtonText,
                      isLeft: true,
                    ),
                    SizedBox(width: 20.w),

                    // 오른쪽 버튼
                    DialogButton(
                      buttonFunc: rightButtonFunc,
                      buttonText: rightButtonText,
                      isLeft: false,
                    ),
                  ],
                )
              ],
            ),
          ),
        ),
      );
    },
  );
}

// 버튼
class DialogButton extends StatelessWidget {
  const DialogButton({
    super.key,
    required this.buttonFunc,
    required this.buttonText,
    required this.isLeft,
  });

  final VoidCallback? buttonFunc;
  final String buttonText;
  final bool isLeft;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 275.w,
      height: 96.h,
      child: TextButton(
        onPressed: buttonFunc,
        style: ButtonStyle(
          backgroundColor: isLeft
              ? WidgetStateProperty.all<Color>(Palette.popupLeftBtnBg)
              : WidgetStateProperty.all<Color>(
                  Palette.popupRightBtnBg,
                ),
          shape: WidgetStateProperty.all<RoundedRectangleBorder>(
            RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(20.r),
            ),
          ),
          minimumSize: WidgetStateProperty.all<Size>(Size(230.w, 104.h)),
        ),
        child: Text(buttonText,
            style: isLeft
                ? Palette.dialogLeftBtnTitle
                : Palette.dialogRightBtnTitle),
      ),
    );
  }
}

/// 사진 삭제 dialog
void showSaveImageDialog(BuildContext context, String imgPath,
    VoidCallback leftButtonFunc, VoidCallback rightButtonFunc) {
  showDialog(
    context: context,
    barrierDismissible: false,
    builder: (BuildContext context) {
      return Dialog(
        insetPadding: EdgeInsets.all(30.w),
        backgroundColor: Colors.white,
        shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.all(Radius.circular(20.r))),
        child: SizedBox(
          height: 850.h,
          width: 650.w,
          child: Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text('사진 저장', style: Palette.dialogContentBold),
                SizedBox(height: 14.h),
                Text(
                  '사진을 저장할까요? 마음에 안드신다면 재촬영이 가능해요.\n재촬영시 아래 사진은 삭제됩니다.',
                  style: Palette.dialogContentSmall,
                ),
                SizedBox(height: 18.h),

                // 이미지
                ClipRRect(
                  borderRadius: BorderRadius.circular(20.r),
                  child: Image.file(File(imgPath),
                      width: 570.w, height: 570.w, fit: BoxFit.fitWidth),
                ),
                // ImageCard(imagePath: Image.file(File(imgPath))),
                SizedBox(height: 55.h),

                // 버튼
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    // 왼쪽 버튼
                    DialogButton(
                      buttonFunc: leftButtonFunc,
                      buttonText: '재촬영',
                      isLeft: true,
                    ),
                    SizedBox(width: 20.w),

                    // 오른쪽 버튼
                    DialogButton(
                      buttonFunc: rightButtonFunc,
                      buttonText: '저장하기',
                      isLeft: false,
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      );
    },
  );
}
