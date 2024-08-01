import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:flutter_svg/svg.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/custom_icon_button.dart';
import 'package:structure/components/home_card.dart';
import 'package:structure/config/pallete.dart';
import 'package:structure/viewModel/home_view_model.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: Padding(
        padding: EdgeInsets.symmetric(horizontal: 40.w),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            SizedBox(height: 95.h),

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
                  image: (context.read<HomeViewModel>().userType == 'Normal')
                      ? 'assets/images/normalperson.svg'
                      // 'assets/images/researcherperson.svg'
                      : (context.read<HomeViewModel>().userType == 'Researcher')
                          ? 'assets/images/managerperson.svg'
                          : 'assets/images/researcherperson.svg',
                  onTap: () =>
                      context.read<HomeViewModel>().clickedMyPage(context),
                  width: 80.w,
                  height: 80.h,
                ),
              ],
            ),
            SizedBox(height: 160.h),

            // 환영 텍스트
            Row(
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('환영합니다.', style: Pallete.h1),
                    Text('원하시는 작업을 선택해주세요.', style: Pallete.h2),
                  ],
                ),
              ],
            ),
            SizedBox(height: 120.h),

            // 육류 등록/관리 버튼
            Row(
              children: [
                // 육류 등록 버튼
                HomeCard(
                  mainText: '육류등록',
                  subText: '\n데이터를 전송합니다',
                  imageUrl: 'assets/images/pig.png',
                  mainColor: Pallete.meatRegiCardBg,
                  btnColor: Pallete.meatRegiBtnBg,
                  subTextStyle: Pallete.h5White,
                  imageWidth: 180.w,
                  imageHeight: 158.h,
                  onTap: () =>
                      context.read<HomeViewModel>().clickedMeatRegist(context),
                ),
                const Spacer(),

                // 데이터 관리 버튼
                HomeCard(
                  mainText: '데이터 관리',
                  subText: '등록된 데이터를\n열람/수정합니다',
                  imageUrl: 'assets/images/chart.png',
                  mainColor: Pallete.dataMngCardBg,
                  btnColor: Pallete.dataMngBtndBg,
                  subTextStyle: Pallete.h5Grey,
                  imageWidth: 200.w,
                  imageHeight: 200.h,
                  onTap: () =>
                      context.read<HomeViewModel>().clickedDataManage(context),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
