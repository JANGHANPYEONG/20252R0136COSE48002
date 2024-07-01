import 'package:flutter/material.dart';

import 'package:flutter_screenutil/flutter_screenutil.dart';

import 'package:go_router/go_router.dart';
import 'package:structure/config/pallete.dart';

class CustomAppBar extends StatelessWidget implements PreferredSizeWidget {
  final String title;
  final bool backButton;
  final bool closeButton;
  final VoidCallback? backButtonOnPressed;
  final VoidCallback? closeButtonOnPressed;
  final bool? centerTitle;
  final double? top;

  const CustomAppBar({
    super.key,
    required this.title,
    required this.backButton,
    required this.closeButton,
    this.backButtonOnPressed,
    this.closeButtonOnPressed,
    this.centerTitle,
    this.top,
  });

  @override
  Widget build(BuildContext context) {
    return AppBar(
      elevation: 0,
      automaticallyImplyLeading: false,
      leading: backButton
          ? IconButton(
              onPressed: backButtonOnPressed ??
                  () {
                    FocusScope.of(context).unfocus();
                    context.pop();
                  },
              icon: const Icon(Icons.arrow_back_ios))
          : null,
      foregroundColor: Palette.appBarIcon,
      centerTitle: centerTitle,
      title: Transform.translate(
        offset: Offset(-50.w, 0), // 왼쪽으로 이동시킬 픽셀 값
        child: Text(
          title,
          style: Palette.appBarTitle,
        ),
      ),
      actions: closeButton
          ? [
              Container(
                margin: EdgeInsets.only(
                  right: 45.w,
                  top: top ?? 39.h,
                ),
                child: Row(
                  children: [
                    InkWell(
                        onTap: closeButtonOnPressed ??
                            () {
                              FocusScope.of(context).unfocus();
                              context.pop();
                            },
                        child: const Icon(Icons.arrow_back)),
                  ],
                ),
              ),
            ]
          : null,
      backgroundColor: Colors.white,
    );
  }

  @override
  Size get preferredSize => const Size.fromHeight(kToolbarHeight);
}
