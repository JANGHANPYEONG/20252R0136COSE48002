import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:structure/config/pallete.dart';

class RoundButton extends StatelessWidget {
  final Text text;
  final void Function()? onPress;
  final double width;
  final double height;
  final Color? bgColor;
  final Color? fgColor;
  const RoundButton({
    super.key,
    required this.text,
    required this.onPress,
    required this.width,
    required this.height,
    this.bgColor,
    this.fgColor,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: width,
      height: height,
      child: ElevatedButton(
        onPressed: onPress,
        style: ElevatedButton.styleFrom(
          elevation: 0,
          foregroundColor: fgColor,
          backgroundColor: bgColor ?? Pallete.mainButtonColor,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20.r),
            side: fgColor != null
                ? const BorderSide(color: Colors.black)
                : BorderSide.none,
          ),
        ),
        child: Center(child: text),
      ),
    );
  }
}
