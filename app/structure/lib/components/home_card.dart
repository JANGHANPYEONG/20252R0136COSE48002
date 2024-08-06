import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:structure/config/palette.dart';

class HomeCard extends StatelessWidget {
  final String mainText;
  final String subText;
  final String imageUrl;
  final Color mainColor;
  final Color btnColor;
  final TextStyle subTextStyle;
  final double imageWidth;
  final double imageHeight;
  final Function()? onTap;

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
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(150.r),
      child: Stack(
        children: [
          Container(
            margin: EdgeInsets.all(8.w),
            width: 304.w,
            height: 544.h,
            decoration: BoxDecoration(
                color: mainColor, borderRadius: BorderRadius.circular(150.r)),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                SizedBox(height: 32.h),

                // 아이콘 원
                Container(
                  width: 240.w,
                  height: 240.w,
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.7),
                    shape: BoxShape.circle,
                  ),
                  child: Center(
                    child: Image.asset(
                      imageUrl,
                      width: imageWidth,
                      height: imageHeight,
                    ),
                  ),
                ),
                SizedBox(height: 24.h),

                // 제목, 설명
                Container(
                  margin: EdgeInsets.only(left: 32.w),
                  alignment: Alignment.centerLeft,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(mainText, style: Palette.h3),
                      SizedBox(height: 16.h),
                      Text(subText, style: subTextStyle),
                    ],
                  ),
                )
              ],
            ),
          ),

          // 하단 화살표
          Transform.translate(
            offset: Offset(144.w, 432.h),
            child: Container(
              width: 160.w,
              height: 80.h,
              padding: EdgeInsets.only(right: 20.w),
              alignment: Alignment.centerRight,
              decoration: BoxDecoration(
                color: btnColor,
                borderRadius: BorderRadius.circular(60.r),
              ),
              child: Icon(
                Icons.arrow_forward,
                size: 50.w,
                color: Colors.white,
              ),
            ),
          )
        ],
      ),
    );
  }
}
