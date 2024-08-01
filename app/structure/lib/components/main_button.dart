import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:structure/config/pallete.dart';

class MainButton extends StatelessWidget {
  final int mode; // mode 0: sign-in, mode1: other else
  final VoidCallback? onPressed;
  final String text;
  final double width;
  final double height;
  final TextStyle? style;

  const MainButton(
      {super.key,
      this.mode = 1,
      this.onPressed,
      required this.text,
      required this.width,
      required this.height,
      this.style});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: width,
      height: height,
      child: ElevatedButton(
        onPressed: onPressed,
        style: ElevatedButton.styleFrom(
          disabledBackgroundColor: Pallete.mainBtnDisabBg,
          backgroundColor: mode == 0 ? Colors.black : Pallete.mainBtnAtvBg,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20.r),
          ),
          elevation: 0,
        ),
        child: Center(
          child: Text(text, style: style ?? Pallete.mainBtnTitle),
        ),
      ),
    );
  }
}
