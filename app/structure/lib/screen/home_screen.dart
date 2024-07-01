import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:flutter_svg/svg.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/custom_icon_button.dart';
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
            SizedBox(
              height: 95.h,
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                SvgPicture.asset(
                  'assets/images/deepaging_logo.svg',
                  width: 220.w,
                ),
                const Spacer(),
                CustomIconButton(
                  image: 'assets/images/person.svg',
                  onTap: () =>
                      context.read<HomeViewModel>().clickedMyPage(context),
                  width: 80.w,
                  height: 80.h,
                ),
              ],
            ),
            SizedBox(
              height: 160.h,
            ),
            Row(
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('환영합니다.', style: Palette.h1),
                    Text('원하시는 작업을 선택해주세요.', style: Palette.h2),
                  ],
                ),
              ],
            ),
            SizedBox(
              height: 120.h,
            ),
            Row(
              children: [
                // 육류 등록 버튼
                InkWell(
                  onTap: () =>
                      context.read<HomeViewModel>().clickedMeatRegist(context),
                  child: HomeCard(
                    mainText: '육류등록',
                    subText: '육류 정보를 입력하고\n데이터를 전송합니다',
                    imageUrl: 'assets/images/pig.png',
                    mainColor: Palette.meatRegiCardBg,
                    btnColor: Palette.meatRegiBtnBg,
                    subTextStyle: Palette.h5White,
                    imageWidth: 179.w,
                    imageHeight: 158.h,
                  ),
                ),
                const Spacer(),
                InkWell(
                  onTap: () =>
                      context.read<HomeViewModel>().clickedDataManage(context),
                  child: HomeCard(
                    mainText: '데이터 관리',
                    subText: '등록된 데이터를\n열람/수정합니다',
                    imageUrl: 'assets/images/chart.png',
                    mainColor: Palette.dataMngCardBg,
                    btnColor: Palette.dataMngBtndBg,
                    subTextStyle: Palette.h5Grey,
                    imageWidth: 200.w,
                    imageHeight: 200.h,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class HomeCard extends StatelessWidget {
  const HomeCard({
    super.key,
    required this.mainText,
    required this.subText,
    required this.imageUrl,
    required this.mainColor,
    required this.btnColor,
    required this.subTextStyle,
    required this.imageWidth,
    required this.imageHeight,
  });
  final String mainText;
  final String subText;
  final String imageUrl;
  final Color mainColor;
  final Color btnColor;
  final TextStyle subTextStyle;
  final double imageWidth;
  final double imageHeight;

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        Container(
          width: 300.w,
          height: 538.h,
          decoration: BoxDecoration(
              color: mainColor,
              borderRadius: BorderRadius.all(Radius.circular(150.sp))),
          child: Column(children: [
            SizedBox(
              height: 31.h,
            ),
            Container(
              width: 238.w,
              height: 238.h,
              decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.7), shape: BoxShape.circle),
              child: Center(
                child: Image.asset(
                  imageUrl,
                  width: imageWidth,
                  height: imageHeight,
                ),
              ),
            ),
            SizedBox(
              height: 31.h,
            ),
            Row(
              children: [
                SizedBox(
                  width: 31.w,
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      mainText,
                      style: Palette.h3,
                    ),
                    SizedBox(
                      height: 10.h,
                    ),
                    Text(
                      subText,
                      style: subTextStyle,
                    ),
                  ],
                ),
              ],
            ),
          ]),
        ),
        Transform.translate(
          offset: Offset(148.w, 425.h),
          child: Container(
            width: 164.w,
            height: 80.h,
            padding: EdgeInsets.only(right: 20.w),
            alignment: Alignment.centerRight,
            decoration: BoxDecoration(
                color: btnColor,
                borderRadius: BorderRadius.all(Radius.circular(50.sp))),
            child: Icon(
              Icons.arrow_forward,
              size: 50.w,
              color: Colors.white,
            ),
          ),
        )
      ],
    );
  }
}
