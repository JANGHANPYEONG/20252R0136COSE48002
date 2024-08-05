import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:structure/config/pallete.dart';

class CamShutter extends StatelessWidget {
  final bool isReady;

  const CamShutter({super.key, required this.isReady});

  @override
  Widget build(BuildContext context) {
    return Stack(
      alignment: Alignment.center,
      children: [
        Image.asset(
          'assets/images/cam-shutter.png',
          width: 104.w,
          height: 104.w,
        ),
        Image.asset(
          'assets/images/cam-shutter-out.png',
          width: 130.w,
          height: 130.w,
          color: isReady ? Pallete.fieldAtvBorder : Pallete.alertColor,
        ),
        Image.asset(
          'assets/images/cam-shutter-in.png',
          width: 42.w,
          height: 42.w,
          color: isReady ? Pallete.fieldAtvBorder : Pallete.alertColor,
        ),
      ],
    );
  }
}
