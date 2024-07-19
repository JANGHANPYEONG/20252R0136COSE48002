import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:flutter_svg/svg.dart';

class CustomIconButton extends StatelessWidget {
  final String image;
  final VoidCallback onTap;
  final double width;
  final double height;

  const CustomIconButton({
    super.key,
    required this.image,
    required this.onTap,
    required this.width,
    required this.height,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(180.r),
      child: Container(
        margin: EdgeInsets.all(8.w),
        decoration: const BoxDecoration(
          shape: BoxShape.circle,
          color: Colors.transparent,
        ),
        child: SvgPicture.asset(
          image,
          width: width,
          height: height,
        ),
      ),
    );
  }
}
