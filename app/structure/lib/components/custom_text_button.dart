import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:structure/config/palette.dart';

class CustomTextButton extends StatelessWidget {
  final String title;
  final VoidCallback? onPressed;
  final TextStyle? textStyle;

  const CustomTextButton({
    super.key,
    required this.title,
    this.onPressed,
    this.textStyle,
  });

  @override
  Widget build(BuildContext context) {
    return TextButton(
      style: TextButton.styleFrom(
        minimumSize: Size.zero,
        padding: EdgeInsets.zero,
      ),
      onPressed: onPressed,
      child: Container(
        padding: EdgeInsets.all(16.w),
        child: Text(title, style: textStyle ?? Palette.h5OnSecondary),
      ),
    );
  }
}
