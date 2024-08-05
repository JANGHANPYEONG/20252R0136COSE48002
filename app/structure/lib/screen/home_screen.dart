import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:flutter_svg/svg.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/custom_icon_button.dart';
import 'package:structure/components/home_card.dart';
import 'package:structure/config/palette.dart';
import 'package:structure/viewModel/home_view_model.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    HomeViewModel homeViewModel = context.watch<HomeViewModel>();

    return Scaffold(
      body: Container(
        margin: EdgeInsets.symmetric(horizontal: 40.w),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            SizedBox(height: 96.h),

            // 상단 타이틀 area
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                // 왼쪽 로고
                SvgPicture.asset(
                  'assets/images/deepaging_logo.svg',
                  width: 220.w,
                ),
                const Spacer(),

                // 오른쪽 마이페이지 아이콘
                CustomIconButton(
                  image: homeViewModel.userType == 'Normal'
                      ? 'assets/images/normalperson.svg'
                      : homeViewModel.userType == 'Researcher'
                          ? 'assets/images/managerperson.svg'
                          : 'assets/images/researcherperson.svg',
                  onTap: () => homeViewModel.clickedMyPage(context),
                  width: 80.w,
                  height: 80.h,
                ),
              ],
            ),

            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  // 환영 텍스트
                  Text('환영합니다.', style: Palette.h1),
                  Text('원하시는 작업을 선택해주세요.', style: Palette.h2),
                  SizedBox(height: 112.h),

                  // 육류 등록/관리 버튼
                  Row(
                    children: [
                      // 육류 등록 버튼
                      HomeCard(
                        mainText: '육류등록',
                        subText: '데이터를 전송합니다',
                        imageUrl: 'assets/images/pig.png',
                        mainColor: Palette.primaryContainer,
                        btnColor: Palette.primary,
                        subTextStyle: Palette.h5.copyWith(color: Colors.white),
                        imageWidth: 180.w,
                        imageHeight: 158.h,
                        onTap: () => homeViewModel.clickedMeatRegist(context),
                      ),
                      const Spacer(),

                      // 데이터 관리 버튼
                      HomeCard(
                        mainText: '데이터 관리',
                        subText: '등록된 데이터를\n열람/수정합니다',
                        imageUrl: 'assets/images/chart.png',
                        mainColor: Palette.onPrimary,
                        btnColor: Colors.black,
                        subTextStyle: Palette.h5Secondary,
                        imageWidth: 200.w,
                        imageHeight: 200.h,
                        onTap: () => homeViewModel.clickedDataManage(context),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
