import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:structure/config/pallete.dart';

class DateContainer extends StatelessWidget {
  final String dateString;
  final bool dateStatus;
  final bool showDecoration;
  final Function()? onTap;

  const DateContainer({
    super.key,
    required this.dateString,
    required this.dateStatus,
    required this.showDecoration,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      splashColor: Colors.transparent,
      highlightColor: Colors.transparent,
      child: Container(
        width: 290.w,
        height: 64.h,
        decoration: BoxDecoration(
          color: dateStatus ? Palette.fieldEmptyBg : Palette.dataMngCardBg,
          borderRadius: BorderRadius.circular(20.r),
          border: showDecoration
              ? Border.all(color: Palette.checkSpeciesColor)
              : null,
        ),
        alignment: Alignment.centerLeft,
        padding: EdgeInsets.only(left: 10.w),
        child: Text(
          dateString,
          style: dateStatus ? Palette.h5 : Palette.h5LightGrey,
        ),
      ),
    );
  }
}
