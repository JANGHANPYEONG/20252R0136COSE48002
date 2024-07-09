import 'package:structure/config/pallete.dart';
import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';

class CustomTableBar extends StatelessWidget {
  const CustomTableBar({super.key, required this.isNormal});
  final bool isNormal;

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.grey[50],
      padding: EdgeInsets.only(top: 18.h),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              SizedBox(
                width: 50.w,
              ),
              SizedBox(
                width: 200.w,
                child: Text('관리번호', style: Palette.h5),
              ),
              const Spacer(),
              SizedBox(
                width: 150.w,
                child: Text(isNormal ? '날짜' : '작성자', style: Palette.h5),
              ),
              const Spacer(),
              SizedBox(
                width: 80.w,
                child: Text(isNormal ? '관리' : '날짜', style: Palette.h5),
              ),
              SizedBox(
                width: 100.w,
              )
            ],
          ),
          Container(
              margin: EdgeInsets.only(top: 18.h),
              height: 0,
              child: const Divider()),
        ],
      ),
    );
  }
}

class CustomTableNormalBar extends StatelessWidget {
  const CustomTableNormalBar({super.key, required this.isNormal});
  final bool isNormal;

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.grey[50],
      padding: EdgeInsets.only(top: 18.h),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              SizedBox(
                width: 40.w,
              ),
              SizedBox(
                width: 200.w,
                child: Text('관리번호', style: Palette.h5),
              ),
              const Spacer(),
              SizedBox(
                width: 150.w,
                child: Text('날짜', style: Palette.h5),
              ),
              const Spacer(),
              SizedBox(
                width: 80.w,
                child: Text('관리', style: Palette.h5),
              ),
              SizedBox(
                width: 80.w,
              )
            ],
          ),
          Container(
              margin: EdgeInsets.only(top: 18.h),
              height: 0,
              child: const Divider()),
        ],
      ),
    );
  }
}

class CustomTableBarResearcherApprove extends StatelessWidget {
  const CustomTableBarResearcherApprove({super.key, required this.isNormal});
  final bool isNormal;

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.grey[50],
      padding: EdgeInsets.only(top: 18.h),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              SizedBox(
                width: 50.w,
              ),
              SizedBox(
                width: 150.w,
                child: Text('관리번호', style: Palette.h5),
              ),
              const Spacer(),
              SizedBox(
                width: 250.w,
                child: Text('작성자', style: Palette.h5),
              ),
              const Spacer(),
              SizedBox(
                width: 100.w,
                child: Text('승인여부', style: Palette.h5),
              ),
              SizedBox(
                width: 100.w,
              )
            ],
          ),
          Container(
              margin: EdgeInsets.only(top: 18.h),
              height: 0,
              child: const Divider()),
        ],
      ),
    );
  }
}
