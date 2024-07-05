//
//
// Color and TextStyle palette.
//
//

import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';

class Palette {
  static const Color mainTextFieldColor = Color.fromRGBO(232, 232, 232, 1);
  static const Color mainButtonColor = Color.fromRGBO(81, 81, 81, 1);
  static const Color subButtonColor = Color.fromRGBO(175, 175, 175, 1);
  static const Color greyTextColor = Color.fromRGBO(120, 120, 120, 1);
  static const Color alertColor = Color.fromRGBO(255, 73, 73, 1);
  static const Color disabledButtonColor = Color(0xFFC4C4C4);

  //육류 기본정보 화면 종류 배경 색깔
  static const Color basicSpeciesColor = Color(0xFFF9F9F9);
  static const Color checkSpeciesColor = Color(0xFF38C55F);

  //육류 기본정보 화면 종류 글씨 색깔
  static const Color basicSpeciesTextColor = Color(0xFF9F9F9F);
  static const Color checkSpeciesTextColor = Color.fromARGB(255, 255, 255, 255);

  // Updated
  // Color Palette
  static const Color meatRegiCardBg = Color(0xff87e980);
  static const Color meatRegiBtnBg = Color(0xff36c45e);
  static const Color dataMngCardBg = Color(0xfff0f0f0);
  static const Color dataMngBtndBg = Color(0xff000000);

  static const Color appBarIcon = Color(0xff4a4a4a);

  static const Color fieldEmptyBg = Color(0xfff9f9f9);
  static Color fieldDisabBg = const Color(0xff000000).withOpacity(0.5);
  static const Color fieldBorder = Color(0xffeaeaea);
  static const Color fieldAtvBorder = Color(0xff38c55f);
  static const Color fieldAlertBorder = Color(0xfff34e4e);

  static const Color mainBtnAtvBg = Color(0xff38c55f);
  static Color mainBtnDisabBg = const Color(0xff38c55f).withOpacity(0.5);

  static const Color alertBg = Color(0xffff4949);

  static const Color popupLeftBtnBg = Color(0xffeeeeee);
  static const Color popupRightBtnBg = Color(0xff000000);

  static const Color userLevelCardBg = Color(0xffe1dcff);

  static const Color dDayCardBg = Color(0xffe8e5ff);

  static const Color confirmCardBg = Color(0xff38c55f);
  static const Color rejectCardBg = Color(0xffff4949);
  static const Color waitingCardBg = Color(0xff9f9f9f);

  static const Color editableBg = Color(0xff38c55f);
  static const Color notEditableBg = Color(0xffd7d7d7);

  static const Color completeBg = Color(0xffdbf8d9);
  static const Color notCompleteBg = Color(0xffffebeb);

  static const Color starIcon = Color(0xffffe871);
  static const Color loadingIcon = Color(0xff38c55f);
  // Text Style Palette
  static TextStyle h1 = TextStyle(fontSize: 50.sp, fontWeight: FontWeight.w700);
  static TextStyle h2 = TextStyle(fontSize: 40.sp, fontWeight: FontWeight.w700);
  static TextStyle h3 = TextStyle(fontSize: 36.sp, fontWeight: FontWeight.w700);
  static TextStyle h3Green = TextStyle(
      fontSize: 36.sp,
      fontWeight: FontWeight.w700,
      color: const Color(0xff38c55f));
  static TextStyle h4 = TextStyle(fontSize: 30.sp, fontWeight: FontWeight.w600);
  static TextStyle h4Grey = TextStyle(
      fontSize: 30.sp,
      fontWeight: FontWeight.w600,
      color: const Color(0xff4a4a4a));
  static TextStyle h5 = TextStyle(fontSize: 24.sp, fontWeight: FontWeight.w400);
  static TextStyle h5White = TextStyle(
      fontSize: 24.sp,
      fontWeight: FontWeight.w400,
      color: const Color(0xffffffff));
  static TextStyle h5Grey = TextStyle(
      fontSize: 24.sp,
      fontWeight: FontWeight.w400,
      color: const Color(0xff848484));
  static TextStyle h5LightGrey = TextStyle(
      fontSize: 24.sp,
      fontWeight: FontWeight.w400,
      color: const Color(0xff9f9f9f));

  static TextStyle mainBtnTitle = TextStyle(
      fontSize: 36.sp,
      fontWeight: FontWeight.w500,
      color: const Color(0xffffffff));

  static TextStyle fieldTitle = TextStyle(
      fontSize: 24.sp,
      fontWeight: FontWeight.w600,
      color: const Color(0xff4a4a4a));
  static TextStyle fieldContent =
      TextStyle(fontSize: 30.sp, fontWeight: FontWeight.w400);
  static TextStyle fieldContentGreen = TextStyle(
      fontSize: 30.sp,
      fontWeight: FontWeight.w600,
      color: const Color(0xff38c55f));
  static TextStyle fieldPlaceHolder = TextStyle(
      fontSize: 30.sp,
      fontWeight: FontWeight.w400,
      color: const Color(0xff9f9f9f));
  static TextStyle fieldPlaceHolderWhite = TextStyle(
      fontSize: 30.sp,
      fontWeight: FontWeight.w400,
      color: const Color(0xffffffff));
  static TextStyle fieldDetail = TextStyle(
      fontSize: 20.sp,
      fontWeight: FontWeight.w400,
      color: const Color(0xff9f9f9f));
  static TextStyle fieldAlert = TextStyle(
      fontSize: 20.sp,
      fontWeight: FontWeight.w400,
      color: const Color(0xfff34e4e));
  static TextStyle userInfoIndex =
      TextStyle(fontSize: 24.sp, fontWeight: FontWeight.w600);
  static TextStyle userInfoTitle = TextStyle(
      fontSize: 20.sp,
      fontWeight: FontWeight.w600,
      color: const Color(0xff9f9f9f));
  static TextStyle userInfoContent = TextStyle(
      fontSize: 24.sp,
      fontWeight: FontWeight.w400,
      color: const Color(0xff4a4a4a));
  static TextStyle userLevelText = TextStyle(
      fontSize: 16.sp,
      fontWeight: FontWeight.w600,
      color: const Color(0xff816cff));

  static TextStyle appBarTitle = TextStyle(
      fontSize: 30.sp,
      fontWeight: FontWeight.w600,
      color: const Color(0xff4a4a4a));

  static TextStyle popupContent =
      TextStyle(fontSize: 32.sp, fontWeight: FontWeight.w400);
  static TextStyle popupBtn = TextStyle(
      fontSize: 24.sp,
      fontWeight: FontWeight.w400,
      color: const Color(0xff38c55f));
  static TextStyle dialogContentBold =
      TextStyle(fontSize: 30.sp, fontWeight: FontWeight.w600);
  static TextStyle dialogContentSmall = TextStyle(
      fontSize: 24.sp,
      fontWeight: FontWeight.w600,
      color: const Color(0xff9f9f9f));
  static TextStyle dialogContentSmallUnderline = TextStyle(
    fontSize: 24.sp,
    fontWeight: FontWeight.w600,
    color: const Color(0xff9f9f9f),
    decoration: TextDecoration.underline,
  );
  static TextStyle dialogLeftBtnTitle = TextStyle(
      fontSize: 30.sp,
      fontWeight: FontWeight.w600,
      color: const Color(0xff4a4a4a));
  static TextStyle dialogRightBtnTitle =
      TextStyle(fontSize: 30.sp, fontWeight: FontWeight.w600);

  static TextStyle completeText = TextStyle(
      fontSize: 20.sp,
      fontWeight: FontWeight.w700,
      color: const Color(0xff38c55f));
  static TextStyle notCompleteText = TextStyle(
      fontSize: 20.sp,
      fontWeight: FontWeight.w700,
      color: const Color(0xffff4949));
  static TextStyle editableText = TextStyle(
      fontSize: 20.sp,
      fontWeight: FontWeight.w700,
      color: const Color(0xffffffff));
  static TextStyle notEditableText = TextStyle(
      fontSize: 20.sp,
      fontWeight: FontWeight.w700,
      color: const Color(0xff9f9f9f));
  static TextStyle seqNoText = TextStyle(
      fontSize: 20.sp,
      fontWeight: FontWeight.w600,
      color: const Color(0xff816cff));
  static TextStyle completeTextLarge = TextStyle(
      fontSize: 24.sp,
      fontWeight: FontWeight.w600,
      color: const Color(0xff38c55f));
  static TextStyle notCompleteTextLarge = TextStyle(
      fontSize: 24.sp,
      fontWeight: FontWeight.w600,
      color: const Color(0xffff4949));

  static TextStyle mngNum =
      TextStyle(fontSize: 45.sp, fontWeight: FontWeight.w700);
  static TextStyle dataListBar = TextStyle(
      fontSize: 20.sp,
      fontWeight: FontWeight.w500,
      color: const Color(0xff6d6c6c));
  static TextStyle dataListMngNum = TextStyle(
      fontSize: 24.sp,
      fontWeight: FontWeight.w400,
      color: const Color(0xff4a4a4a));
  static TextStyle dataListdate = TextStyle(
      fontSize: 20.sp,
      fontWeight: FontWeight.w400,
      color: const Color(0xff9f9f9f));
  static TextStyle dataListUserId = TextStyle(
      fontSize: 20.sp,
      fontWeight: FontWeight.w400,
      color: const Color(0xff9f9f9f));

  static TextStyle dDayText = TextStyle(
      fontSize: 10.sp,
      fontWeight: FontWeight.w600,
      color: const Color(0xff816cff));

  static TextStyle filterTitle = TextStyle(
      fontSize: 20.sp,
      fontWeight: FontWeight.w600,
      color: const Color(0xff4a4a4a));
  static TextStyle filterContent = TextStyle(
      fontSize: 24.sp,
      fontWeight: FontWeight.w400,
      color: const Color(0xff9f9f9f));
  static TextStyle filterContentGreen = TextStyle(
      fontSize: 24.sp,
      fontWeight: FontWeight.w400,
      color: const Color(0xff38c55f));

  //listView에 사용되는 textstyle
  static TextStyle listIndexGrey = TextStyle(
      fontSize: 24.sp,
      fontWeight: FontWeight.w700,
      color: const Color(0xff848484)); //
  static TextStyle listStyle = TextStyle(
      fontSize: 30.sp,
      fontWeight: FontWeight.w600,
      color: const Color(0xff4a4a4a));
  static TextStyle mainTextFieldTextStyle = TextStyle(
      fontSize: 35.sp,
      fontWeight: FontWeight.w700,
      color: const Color(0xFF9F9F9F));
  static TextStyle dropDownTitleStyle = TextStyle(
      fontSize: 33.sp,
      fontWeight: FontWeight.w700,
      color: const Color(0xFF9F9F9F));
  static TextStyle dropDownTextStyle = TextStyle(
      fontSize: 33.sp,
      fontWeight: FontWeight.w700,
      color: const Color.fromARGB(255, 0, 0, 0));
  static TextStyle selectSpeciesStyle = TextStyle(
      fontSize: 33.sp,
      fontWeight: FontWeight.w700,
      color: const Color.fromARGB(255, 255, 255, 255));
}
