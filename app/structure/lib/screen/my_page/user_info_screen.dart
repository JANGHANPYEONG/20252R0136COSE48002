import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/custom_app_bar.dart';
import 'package:structure/components/main_button.dart';
import 'package:structure/config/pallete.dart';
import 'package:structure/viewModel/my_page/user_info_view_model.dart';

class UserInfoScreen extends StatelessWidget {
  const UserInfoScreen({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: const CustomAppBar(
          title: '마이페이지', backButton: true, closeButton: false),
      body: Center(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            SizedBox(height: 20.h),

            // 기본 정보
            Container(
              margin: EdgeInsets.only(left: 40.w),
              alignment: Alignment.centerLeft,
              child: Text(
                '기본정보',
                style: Palette.userInfoIndex,
              ),
            ),
            SizedBox(height: 20.h),
            SizedBox(
              width: 640.w,
              child: Row(
                children: [
                  SizedBox(
                    width: 82.w,
                    child: Text(
                      '이름',
                      style: Palette.userInfoTitle,
                    ),
                  ),
                  SizedBox(
                    width: 340.w,
                    child: SingleChildScrollView(
                      scrollDirection: Axis.horizontal,
                      child: Row(
                        children: [
                          Text(
                            context.read<UserInfoViewModel>().userName,
                            style: Palette.userInfoContent,
                          ),
                          SizedBox(width: 8.w),
                          Container(
                            height: 34.h,
                            alignment: Alignment.center,
                            padding: EdgeInsets.symmetric(horizontal: 13.w),
                            decoration: BoxDecoration(
                                color: Palette.userLevelCardBg,
                                borderRadius:
                                    BorderRadius.all(Radius.circular(28.5.sp))),
                            child: Text(
                              context.read<UserInfoViewModel>().userType,
                              style: Palette.userLevelText,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  SizedBox(width: 10.w),
                ],
              ),
            ),
            SizedBox(height: 20.h),
            SizedBox(
              width: 640.w,
              child: Row(
                children: [
                  SizedBox(
                    width: 82.w,
                    child: Text(
                      "가입일",
                      style: Palette.userInfoTitle,
                    ),
                  ),
                  Text(
                    context.read<UserInfoViewModel>().createdAt,
                    style: Palette.userInfoContent,
                  ),
                ],
              ),
            ),
            SizedBox(height: 20.h),
            SizedBox(
              width: 640.w,
              child: Row(
                children: [
                  SizedBox(
                      width: 82.w,
                      child: Text(
                        '이메일',
                        style: Palette.userInfoTitle,
                      )),
                  Text(
                    context.read<UserInfoViewModel>().userId,
                    style: Palette.userInfoContent,
                  ),
                ],
              ),
            ),
            SizedBox(height: 20.h),
            Container(
              margin: EdgeInsets.symmetric(horizontal: 40.w),
              child: const Divider(
                height: 0,
              ),
            ),

            // 상세 정보
            InkWell(
              onTap: () =>
                  context.read<UserInfoViewModel>().clickedEdit(context),
              child: SizedBox(
                width: 640.w,
                height: 90.h,
                child: Row(
                  children: [
                    Text(
                      '상세정보',
                      style: Palette.userInfoIndex,
                    ),
                    const Spacer(),
                    Icon(
                      Icons.arrow_forward_ios,
                      color: Palette.appBarIcon,
                      size: 24.h,
                    )
                  ],
                ),
              ),
            ),
            SizedBox(
              width: 640.w,
              child: Row(
                children: [
                  SizedBox(
                      width: 82.w,
                      child: Text(
                        '주소',
                        style: Palette.userInfoTitle,
                      )),
                  SizedBox(
                    width: 547.w,
                    child: SingleChildScrollView(
                      scrollDirection: Axis.horizontal,
                      child: Text(
                        context.read<UserInfoViewModel>().homeAdress,
                        style: Palette.userInfoContent,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            SizedBox(height: 20.h),
            SizedBox(
              width: 640.w,
              child: Row(
                children: [
                  SizedBox(
                      width: 82.w,
                      child: Text(
                        '회사명',
                        style: Palette.userInfoTitle,
                      )),
                  Text(
                    context.read<UserInfoViewModel>().company,
                    style: Palette.userInfoContent,
                  ),
                ],
              ),
            ),
            SizedBox(height: 20.h),
            SizedBox(
              width: 640.w,
              child: Row(
                children: [
                  SizedBox(
                    width: 82.w,
                    child: Text(
                      '부서명',
                      style: Palette.userInfoTitle,
                    ),
                  ),
                  SizedBox(
                    width: 247.w,
                    child: Text(
                      context.read<UserInfoViewModel>().department,
                      style: Palette.userInfoContent,
                    ),
                  ),
                  SizedBox(
                    width: 102.w,
                    child: Text(
                      "직위",
                      style: Palette.userInfoTitle,
                    ),
                  ),
                  Text(
                    context.read<UserInfoViewModel>().jobTitle,
                    style: Palette.userInfoContent,
                  ),
                ],
              ),
            ),
            SizedBox(height: 40.h),
            Container(
              margin: EdgeInsets.symmetric(horizontal: 40.w),
              child: const Divider(
                height: 0,
              ),
            ),

            // 비밀번호 변경
            InkWell(
              onTap: () =>
                  context.read<UserInfoViewModel>().clickedChangePW(context),
              child: SizedBox(
                width: 640.w,
                height: 90.h,
                child: Row(
                  children: [
                    Text(
                      '비밀번호 변경',
                      style: Palette.userInfoIndex,
                    ),
                    const Spacer(),
                    Icon(
                      Icons.arrow_forward_ios,
                      color: Palette.appBarIcon,
                      size: 24.h,
                    )
                  ],
                ),
              ),
            ),
            Container(
              margin: EdgeInsets.symmetric(horizontal: 40.w),
              child: const Divider(
                height: 0,
              ),
            ),

            // 회원 탈퇴
            InkWell(
              onTap: () =>
                  context.read<UserInfoViewModel>().clickedChangePW(context),
              child: SizedBox(
                width: 640.w,
                height: 90.h,
                child: Row(
                  children: [
                    Text(
                      '회원 탈퇴',
                      style: Palette.userInfoIndex,
                    ),
                    const Spacer(),
                    Icon(
                      Icons.arrow_forward_ios,
                      color: Palette.appBarIcon,
                      size: 24.h,
                    )
                  ],
                ),
              ),
            ),
            Container(
              margin: EdgeInsets.symmetric(horizontal: 40.w),
              child: const Divider(
                height: 0,
              ),
            ),
            const Spacer(),

            // 로그아웃 버튼
            Container(
              margin: EdgeInsets.only(bottom: 40.h),
              child: MainButton(
                mode: 1,
                text: '로그아웃',
                width: 640.w,
                height: 96.h,
                onPressed: () async =>
                    context.read<UserInfoViewModel>().clickedSignOut(context),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
