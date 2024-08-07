import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:go_router/go_router.dart';
import 'package:structure/config/palette.dart';

class CustomAppBar extends StatelessWidget implements PreferredSizeWidget {
  final String title;
  final bool backButton;
  final bool closeButton;
  final VoidCallback? backButtonOnPressed;
  final VoidCallback? closeButtonOnPressed;
  final bool? centerTitle;
  final double? top;
  final TabController? tabController;
  final List<Tab>? tabs;
  final Widget? actionButton;

  const CustomAppBar({
    super.key,
    required this.title,
    this.backButton = false,
    this.closeButton = false,
    this.backButtonOnPressed,
    this.closeButtonOnPressed,
    this.centerTitle,
    this.top,
    this.tabController,
    this.tabs,
    this.actionButton,
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
              icon: const Icon(Icons.arrow_back_ios),
            )
          : null,
      foregroundColor: Palette.secondary,
      centerTitle: centerTitle,
      title: Transform.translate(
        offset: Offset(-48.w, 0), // 왼쪽으로 이동시킬 픽셀 값
        child: Text(
          title,
          style: Palette.h4Secondary,
        ),
      ),
      actions: [
        if (closeButton)
          Container(
            margin: EdgeInsets.only(
              right: 48.w,
              top: top ?? 40.h,
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

        // 기타 액션 버튼
        actionButton ?? Container(),
      ],
      bottom: tabController != null
          ? TabBar(
              indicatorColor: Palette.primary,
              labelColor: Colors.black,
              controller: tabController,
              tabs: tabs ?? [],
            )
          : null,
      backgroundColor: Colors.white,
    );
  }

  @override
  Size get preferredSize {
    final tabBarHeight = tabController != null ? kTextTabBarHeight : 0.0;
    return Size.fromHeight(kToolbarHeight + tabBarHeight);
  }
}
