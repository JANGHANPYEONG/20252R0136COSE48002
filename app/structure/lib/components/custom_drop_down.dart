//
//
// CustomDropDown 위젯.
// 데이터 등록 과정 중, 육류 분류를 지정할 때 사용된다.
//
// 파라미터로는
// 1. 현재 분류 값이 표시될 위젯 (대분류 / 소분류 텍스트가 들어감.)
// 2. 선택된 값이 표시될 텍스트 (현재 선택된 분류 값)
// 3. 분류 목록 (각 분류에 맞는 목록이 들어간 리스트)
// 4. DropDown 위젯을 선택할 때, 기능을 수행할 함수
//
//

import 'package:structure/config/pallete.dart';
import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';

class CustomDropdown extends StatelessWidget {
  final Widget hintText;
  final String? value;
  final List<String> itemList;
  final Function(String?)? onChanged;

  const CustomDropdown({
    super.key,
    required this.hintText,
    required this.value,
    required this.itemList,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Palette.fieldEmptyBg,
        borderRadius: BorderRadius.circular(15.sp),
        border: Border.all(
          color: value != null ? Palette.meatRegiCardBg : Palette.fieldEmptyBg,
          width: 1.0,
        ),
      ),
      child: DropdownButton(
        padding: EdgeInsets.only(left: 40.w),
        alignment: Alignment.centerLeft,
        elevation: 1,
        // 밑줄을 표현하기 위해 사용.
        underline: Container(),
        borderRadius: BorderRadius.circular(15.sp),
        dropdownColor: Colors.white,
        menuMaxHeight: 310.h,
        // 우측의 화살표 버튼을 추가하기 위해 사용.
        icon: Container(
          width: 20.w,
          margin: EdgeInsets.only(right: 30.w),
          child: Image.asset('assets/images/arrow-b.png'),
        ),
        // 페이지 너비에 맞게 조정.
        isExpanded: true,
        hint: hintText,
        value: value,
        items: itemList
            // itemList를 받아서 'DropdownMenuItem'에 맞게 매핑한다.
            .map((e) => DropdownMenuItem(
                  value: e,
                  child: Text(e, style: Palette.h4),
                ))
            .toList(),
        onChanged: onChanged,
      ),
    );
  }
}
