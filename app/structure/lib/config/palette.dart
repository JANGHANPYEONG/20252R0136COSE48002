import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';

class Palette {
  /* 색 관련 변수 */
  // Primary 색 (초록)
  static const Color primary = Color(0xFF38C55F);

  // Primary 색 위에 올라가는 텍스트 색상
  static const Color onPrimary = Color(0xFFE8E8E8);

  // Primary continaer 색 (연초록)
  static const Color primaryContainer = Color(0xFF87E980);

  static const Color onPrimaryContainer = Color(0xFFF9F9F9);

  // Secondary 색 (회색)
  static const Color secondary = Color(0xFF515151);
  static const Color onSecondary = Color(0xFF9F9F9F);

  // Error 색 (빨강)
  static const Color error = Color(0xFFFF4949);

  // 기타 색
  static const Color starYellow = Color(0xFFFFE871);

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

  /// Font size: 36.sp
  /// <br /> Font weight: w400
  static TextStyle h3Regular = TextStyle(
    fontSize: 36.sp,
    fontWeight: FontWeight.w400,
    color: Colors.black,
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
  /// <br /> Font weight: w400
  static TextStyle h4Regular = TextStyle(
    fontSize: 30.sp,
    fontWeight: FontWeight.w400,
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

  /// Font size: 30.sp
  /// <br /> Font weight: w600
  ///   /// <br /> Color: onSecondary
  static TextStyle h4OnSecondary = TextStyle(
    fontSize: 30.sp,
    fontWeight: FontWeight.w600,
    color: onSecondary,
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
  /// <br /> Color: onSecondary
  static TextStyle h5OnSecondary = TextStyle(
    fontSize: 24.sp,
    fontWeight: FontWeight.w400,
    color: onSecondary,
  );

  /// Font size: 24.sp
  /// <br /> Font weight: w600
  /// <br /> Color: onSecondary
  static TextStyle h5SemiBoldOnSecondary = TextStyle(
    fontSize: 24.sp,
    fontWeight: FontWeight.w600,
    color: onSecondary,
  );

  /* h6 */
  /// Font size: 20.sp
  /// <br /> Font weight: w400
  static TextStyle h6 = TextStyle(
    fontSize: 20.sp,
    fontWeight: FontWeight.w400,
    color: Colors.black,
  );

  /// Font size: 20.sp
  /// <br /> Font weight: w600
  /// <br /> Color: onSecondary
  static TextStyle h6SemiBoldOnSecondary = TextStyle(
    fontSize: 20.sp,
    fontWeight: FontWeight.w600,
    color: onSecondary,
  );

  /* h7 */
  /// Font size: 16.sp
  /// <br /> Font weight: w600
  static TextStyle h7 = TextStyle(
    fontSize: 16.sp,
    fontWeight: FontWeight.w400,
    color: Colors.black,
  );
}
