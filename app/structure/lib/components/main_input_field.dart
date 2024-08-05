//
//
// MainInputField 위젯.
// 주로 User 관리에 사용된다.
//
// 파라미터로는
// 1. formkey 지정
// 2. mode 지정 (mode: 0 -> sign-in | mode : 1 -> other else)
// 3. 문자 입력 방식 (패스워드의 경우 obscure: true -> 가림)
// 4. 읽기 전용 방식 (read only)
// 5. 필드 비활성화 (enabled)
// 6. 너비 조정
// 7. 필드 컨트롤러
// 8. validate 를 위한 함수 (유효성 검사)
// 9. onChanged 를 위한 함수 (form의 입력을 감지할 때 호출)
// 10. 텍스트필드 클릭시에 보이는 힌트텍스트
// 11. 필드의 내용 값에 padding 적용.
//
//

import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:structure/config/pallete.dart';

class MainInputField extends StatefulWidget {
  const MainInputField({
    super.key,
    this.formKey,
    this.mode = 1,
    this.obscureText,
    this.readonly,
    this.enable,
    required this.width,
    this.controller,
    this.validateFunc,
    this.onChangeFunc,
    this.hintText,
    this.contentPadding,
  });
  final GlobalKey<FormState>? formKey;
  final int mode; // mode0: sign-in, mode1: other else
  final bool? obscureText;
  final bool? readonly;
  final bool? enable;
  final double width;
  final TextEditingController? controller;
  final String? Function(String?)? validateFunc;
  final void Function(String)? onChangeFunc;
  final String? hintText;
  final EdgeInsetsGeometry? contentPadding;

  @override
  State<MainInputField> createState() => _MainInputFieldState();
}

class _MainInputFieldState extends State<MainInputField> {
  late FocusNode _focusNode;
  bool _isFocused = false;

  @override
  void initState() {
    super.initState();
    _focusNode = FocusNode();
    _focusNode.addListener(_handleFocusChange);
  }

  void _handleFocusChange() {
    if (!_focusNode.hasFocus) {
      widget.formKey?.currentState?.validate();
    }
    if (_focusNode.hasFocus != _isFocused) {
      setState(() {
        _isFocused = _focusNode.hasFocus;
      });
    }
  }

  @override
  void dispose() {
    _focusNode.removeListener(_handleFocusChange);
    _focusNode.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    Color fillColor = widget.mode == 0 ? Colors.white : Pallete.fieldEmptyBg;

    if (_isFocused) {
      fillColor = Colors.white;
    }

    return SizedBox(
      width: widget.width,
      child: TextFormField(
        controller: widget.controller,
        focusNode: _focusNode,
        cursorColor: Pallete.fieldAtvBorder,
        validator: widget.validateFunc,
        onChanged: widget.onChangeFunc,
        style: Pallete.fieldContent,
        obscureText: widget.obscureText ?? false,
        readOnly: widget.readonly ?? false,
        enabled: widget.enable,
        decoration: InputDecoration(
          filled: true,
          fillColor: fillColor,
          hintText: widget.hintText,
          errorBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(15.sp),
            borderSide: const BorderSide(color: Pallete.fieldAlertBorder),
          ),
          focusedErrorBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(15.sp),
            borderSide: const BorderSide(color: Pallete.fieldAlertBorder),
          ),
          errorStyle: Pallete.fieldAlert,
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(15.sp),
            borderSide: BorderSide(
              color:
                  widget.mode == 0 ? Pallete.fieldBorder : Pallete.fieldEmptyBg,
            ),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(20.r),
            borderSide: const BorderSide(color: Pallete.fieldAtvBorder),
          ),
          contentPadding:
              widget.contentPadding ?? EdgeInsets.symmetric(horizontal: 24.w),
        ),
      ),
    );
  }
}
