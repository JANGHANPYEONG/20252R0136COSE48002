//
//
// TextField 위젯.
// 주로 데이터 입력에 사용된다.
//
// 파라미터로는
// 1. validate 를 위한 함수 (유효성 검사)
// 2. onSaved 를 위한 함수 (form의 상태를 저장할 때 호출)
// 3. onChanged 를 위한 함수 (form의 입력을 감지할 때 호출)
// 4. onFieldSubmitted 를 위한 함수 (form의 입력이 완료된 후 다음 동작을 수행할 때 호출)
// 5. 텍스트필드 바탕에 보이는 텍스트
// 6. 텍스트필드 클릭시에 보이는 힌트텍스트
// 7. 너비 조정
// 8. 높이 조정
// 9. 문자 입력 방식 (패스워드의 경우 obscure: true -> 가림)
// 9. 문자 정렬 (Center면 true)
// 10. 에러 표시 (유효성을 검사하는 필드에서 사용)
// 11. 필드 컨트롤러
// 12. 최대 길이 지정
// 13. 텍스트 포맷 지정 (텍스트가 특정 값만 인식함 : 숫자나 문자 등)
// 14. 텍스트 버튼 지정 (완료, 검색 등과 같은 아이콘)
// 15. FocusNode 지정
// 16. 필드 앞에 위치할 아이콘 지정
// 17. 필드 위에 위치할 아이콘 지정
//
//

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:structure/config/pallete.dart';

class MainTextField extends StatelessWidget {
  final String? Function(String?)? validateFunc;
  final void Function(String?)? onSaveFunc;
  final void Function(String?)? onChangeFunc;
  final void Function(String?)? onFieldFunc;
  final String mainText;
  final String? hintText;
  final double width;
  final double height;
  final bool? isObscure;
  final bool? isCenter;
  final bool canAlert;
  final TextEditingController? controller;
  final int? maxLength;
  final List<FilteringTextInputFormatter>? formatter;
  final TextInputAction? action;
  final FocusNode? focusNode;
  final Widget? suffixIcon;
  final Widget? prefixIcon;
  final bool? fillColorAlert; // 클릭했을 때 배경 색 변경

  const MainTextField({
    super.key,
    required this.validateFunc,
    required this.onSaveFunc,
    required this.onChangeFunc,
    this.onFieldFunc,
    required this.mainText,
    this.hintText,
    required this.width,
    required this.height,
    required this.canAlert,
    this.isObscure,
    this.isCenter,
    this.controller,
    this.maxLength,
    this.formatter,
    this.action,
    this.focusNode,
    this.suffixIcon,
    this.prefixIcon,
    this.fillColorAlert,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      // 아이디 입력 필드
      width: width,
      child: TextFormField(
        controller: controller,
        focusNode: focusNode,
        autofocus: false,
        maxLength: maxLength,
        showCursor: false,
        // 유효성 검사
        validator: validateFunc,
        onSaved: onSaveFunc,
        onChanged: onChangeFunc,
        onFieldSubmitted: onFieldFunc,
        inputFormatters: formatter,
        textInputAction: action,
        obscureText: isObscure ?? false,
        decoration: InputDecoration(
            prefixIcon: prefixIcon,
            label: isCenter != null && isCenter == true
                ? Center(
                    child: Text(
                      mainText,
                      style: Palette.h4Grey,
                    ),
                  )
                : Text(
                    mainText,
                    style: Palette.mainTextFieldTextStyle,
                  ),
            filled: true,
            fillColor: Palette.fieldEmptyBg,
            hintText: hintText,
            hintStyle: Palette.h4,
            suffixIcon: suffixIcon,
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(20.w),
              borderSide: BorderSide.none,
            ),
            errorBorder: canAlert
                ? OutlineInputBorder(
                    borderRadius: BorderRadius.circular(15.sp),
                    borderSide:
                        const BorderSide(color: Palette.fieldAlertBorder),
                  )
                : null,
            focusedErrorBorder: canAlert
                ? OutlineInputBorder(
                    borderRadius: BorderRadius.circular(15.sp),
                    borderSide:
                        const BorderSide(color: Palette.fieldAlertBorder),
                  )
                : null,
            enabledBorder: canAlert
                ? OutlineInputBorder(
                    borderRadius: BorderRadius.circular(15.sp),
                    borderSide: BorderSide.none,
                    // borderSide: BorderSide(
                    //   color: Palette.fieldDisabBg,
                    // ),
                  )
                : null,
            focusedBorder: canAlert
                ? OutlineInputBorder(
                    borderRadius: BorderRadius.circular(15.sp),
                    borderSide: const BorderSide(
                      color: Palette.fieldAtvBorder,
                    ),
                  )
                : null,
            contentPadding:
                const EdgeInsets.symmetric(horizontal: 16, vertical: 10)),
      ),
    );
  }
}
