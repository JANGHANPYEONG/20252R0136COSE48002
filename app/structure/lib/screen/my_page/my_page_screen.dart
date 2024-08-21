import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/custom_app_bar.dart';
import 'package:structure/components/custom_divider.dart';
import 'package:structure/components/main_button.dart';
import 'package:structure/config/palette.dart';
import 'package:structure/viewModel/my_page/my_page_view_model.dart';

class MyPageScreen extends StatefulWidget {
  const MyPageScreen({super.key});

  @override
  State<MyPageScreen> createState() => _MyPageScreenState();
}

class _MyPageScreenState extends State<MyPageScreen> {
  @override
  Widget build(BuildContext context) {
    MyPageViewModel myPageViewModel = context.watch<MyPageViewModel>();

    return Scaffold(
      appBar: const CustomAppBar(title: '마이페이지'),
      body: Container(
        margin: EdgeInsets.symmetric(horizontal: 40.w),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            SizedBox(height: 24.h),

            // 기본 정보
            Container(
              padding: EdgeInsets.symmetric(horizontal: 16.w),
              child: Text('기본정보', style: Palette.h5SemiBoldSecondary),
            ),
            SizedBox(height: 16.h),

            Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                // 이름
                Expanded(
                  child: Row(
                    children: [
                      // 이름
                      SizedBox(
                        width: 80.w,
                        child: Text('이름', style: Palette.h6SemiBoldOnSecondary),
                      ),
                      Text(myPageViewModel.userName, style: Palette.h5),
                      SizedBox(width: 16.w),

                      // 직위 컨테이너
                      Container(
                        height: 32.h,
                        alignment: Alignment.center,
                        padding: EdgeInsets.symmetric(horizontal: 16.w),
                        decoration: BoxDecoration(
                          color: myPageViewModel.userType == 'Normal'
                              ? Palette.userNormalCardBg
                              : myPageViewModel.userType != 'Researcher'
                                  ? Palette.userManagerCardBg
                                  : Palette.userResearcherCardBg,
                          borderRadius: BorderRadius.circular(20.r),
                        ),
                        child: Text(
                          myPageViewModel.userType,
                          style: Palette.h7,
                        ),
                      ),
                    ],
                  ),
                ),

                // 가입 날짜
                Expanded(
                  child: Row(
                    children: [
                      SizedBox(
                        width: 80.w,
                        child: Text(
                          "가입날짜",
                          style: Palette.h6SemiBoldOnSecondary,
                        ),
                      ),
                      Text(myPageViewModel.createdAt, style: Palette.h5),
                    ],
                  ),
                )
              ],
            ),
            SizedBox(height: 16.h),

            Row(
              children: [
                SizedBox(
                  width: 80.w,
                  child: Text('이메일', style: Palette.h6SemiBoldOnSecondary),
                ),
                Text(myPageViewModel.userId, style: Palette.h5),
              ],
            ),
            SizedBox(height: 32.h),

            const CustomDivider(),

            // 상세 정보
            InkWell(
              onTap: () {
                myPageViewModel.clickedEdit();
              },
              borderRadius: BorderRadius.circular(20.r),
              child: Container(
                padding: EdgeInsets.symmetric(horizontal: 16.w),
                width: double.infinity,
                height: 80.h,
                child: Row(
                  children: [
                    Text('상세정보', style: Palette.h5SemiBoldSecondary),
                    const Spacer(),
                    Icon(
                      Icons.arrow_forward_ios,
                      color: Palette.secondary,
                      size: 24.h,
                    )
                  ],
                ),
              ),
            ),

            // 주소
            Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                SizedBox(
                  width: 80.w,
                  child: Text('주소', style: Palette.h6SemiBoldOnSecondary),
                ),
                SizedBox(
                  width: 560.w,
                  child: SingleChildScrollView(
                    scrollDirection: Axis.horizontal,
                    child: Text(
                      myPageViewModel.homeAdress,
                      style: Palette.h5,
                    ),
                  ),
                ),
              ],
            ),
            SizedBox(height: 16.h),

            Row(
              children: [
                SizedBox(
                  width: 80.w,
                  child: Text('회사명', style: Palette.h6SemiBoldOnSecondary),
                ),
                Text(
                  myPageViewModel.company,
                  style: Palette.h5,
                ),
              ],
            ),
            SizedBox(height: 16.h),

            Row(
              children: [
                Expanded(
                  child: Row(
                    children: [
                      SizedBox(
                        width: 80.w,
                        child: Text(
                          '부서명',
                          style: Palette.h6SemiBoldOnSecondary,
                        ),
                      ),
                      Text(
                        myPageViewModel.department,
                        style: Palette.h5,
                      ),
                    ],
                  ),
                ),
                Expanded(
                  child: Row(
                    children: [
                      SizedBox(
                        width: 80.w,
                        child: Text(
                          "직위",
                          style: Palette.h6SemiBoldOnSecondary,
                        ),
                      ),
                      Text(
                        myPageViewModel.jobTitle,
                        style: Palette.h5,
                      ),
                    ],
                  ),
                ),
              ],
            ),
            SizedBox(height: 32.h),

            const CustomDivider(),

            // 비밀번호 변경
            InkWell(
              onTap: () => myPageViewModel.clickedChangePW(),
              borderRadius: BorderRadius.circular(20.r),
              child: SizedBox(
                width: double.infinity,
                height: 80.h,
                child: Container(
                  padding: EdgeInsets.symmetric(horizontal: 16.w),
                  child: Row(
                    children: [
                      Text(
                        '비밀번호 변경',
                        style: Palette.h5SemiBoldSecondary,
                      ),
                      const Spacer(),
                      Icon(
                        Icons.arrow_forward_ios,
                        color: Palette.secondary,
                        size: 24.h,
                      )
                    ],
                  ),
                ),
              ),
            ),

            const CustomDivider(),

            // 회원 탈퇴
            InkWell(
              onTap: () => myPageViewModel.clickedDeleteUser(),
              borderRadius: BorderRadius.circular(20.r),
              child: SizedBox(
                width: double.infinity,
                height: 80.h,
                child: Container(
                  padding: EdgeInsets.symmetric(horizontal: 16.w),
                  child: Row(
                    children: [
                      Text(
                        '회원 탈퇴',
                        style: Palette.h5SemiBoldSecondary,
                      ),
                      const Spacer(),
                      Icon(
                        Icons.arrow_forward_ios,
                        color: Palette.secondary,
                        size: 24.h,
                      )
                    ],
                  ),
                ),
              ),
            ),

            const CustomDivider(),

            const Spacer(),

            // 로그아웃 버튼
            Container(
              margin: EdgeInsets.only(bottom: 40.h),
              child: MainButton(
                width: double.infinity,
                height: 96.h,
                text: '로그아웃',
                onPressed: () async => myPageViewModel.clickedSignOut(),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
