import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';

class Palette {
  /* 색 관련 변수 */
  // Primary 색 (초록)
  static const Color primary = Color(0xFF38C55F);
  static Color primary50 = const Color(0xFF38C55F).withOpacity(0.5);

  // Primary 색 위에 올라가는 텍스트 색상
  static const Color onPrimary = Color(0xFFE8E8E8);

  // Secondary 색 (회색)
  static const Color secondary = Color(0xFF515151);
  static Color secondary50 = const Color(0xFF515151).withOpacity(0.5);

  static const Color error = Color(0xFFFF4949);

  /* TextStyle */
  /* h1 */
  /// Font size: 50.sp
  /// <br /> Font weight: w700
  static TextStyle h1 = TextStyle(fontSize: 50.sp, fontWeight: FontWeight.w700);

  /* h2 */
  /// Font size: 40.sp
  /// <br /> Font weight: w700
  static TextStyle h2 = TextStyle(
    fontSize: 40.sp,
    fontWeight: FontWeight.w700,
    color: Colors.black,
  );

  /* h3 */
  /// Font size: 36.sp
  /// <br /> Font weight: w700
  static TextStyle h3 = TextStyle(
    fontSize: 36.sp,
    fontWeight: FontWeight.w700,
    color: Colors.black,
  );

  /// Font size: 36.sp
  /// <br /> Font weight: w700
  /// <br /> Color: primary
  static TextStyle h3Primary = TextStyle(
    fontSize: 36.sp,
    fontWeight: FontWeight.w700,
    color: primary,
  );

  /// Font size: 36.sp
  /// <br /> Font weight: w700
  /// <br /> Color: onPrimary
  static TextStyle h3OnPrimary = TextStyle(
    fontSize: 36.sp,
    fontWeight: FontWeight.w700,
    color: onPrimary,
  );

  /* h4 */
  /// Font size: 30.sp
  /// <br /> Font weight: w600
  static TextStyle h4 = TextStyle(
    fontSize: 30.sp,
    fontWeight: FontWeight.w600,
    color: Colors.black,
  );

  /// Font size: 30.sp
  /// <br /> Font weight: w600
  ///   /// <br /> Color: secondary
  static TextStyle h4Secondary = TextStyle(
    fontSize: 30.sp,
    fontWeight: FontWeight.w600,
    color: secondary,
  );

  /* h5 */
  /// Font size: 24.sp
  /// <br /> Font weight: w400
  static TextStyle h5 = TextStyle(
    fontSize: 24.sp,
    fontWeight: FontWeight.w400,
    color: Colors.black,
  );

  /// Font size: 24.sp
  /// <br /> Font weight: w600
  /// <br /> Color : black
  static TextStyle h5SemiBold = TextStyle(
    fontSize: 24.sp,
    fontWeight: FontWeight.w600,
    color: Colors.black,
  );

  /// Font size: 24.sp
  /// <br /> Font weight: w400
  /// <br /> Color: onPrimary
  static TextStyle h5OnPrimary = TextStyle(
    fontSize: 24.sp,
    fontWeight: FontWeight.w400,
    color: onPrimary,
  );

  /// Font size: 24.sp
  /// <br /> Font weight: w400
  /// <br /> Color: secondary
  static TextStyle h5Secondary = TextStyle(
    fontSize: 24.sp,
    fontWeight: FontWeight.w400,
    color: secondary,
  );

  /// Font size: 24.sp
  /// <br /> Font weight: w600
  /// <br /> Color: secondary
  static TextStyle h5SemiBoldSecondary = TextStyle(
    fontSize: 24.sp,
    fontWeight: FontWeight.w600,
    color: secondary,
  );

  /// Font size: 24.sp
  /// <br /> Font weight: w400
  /// <br /> Color: secondary50
  static TextStyle h5Secondary50 = TextStyle(
    fontSize: 24.sp,
    fontWeight: FontWeight.w400,
    color: secondary50,
  );
}
