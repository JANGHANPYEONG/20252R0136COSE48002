//
//
// InnerBox 위젯.
// insertion_trace_num의 table을 구성하는 요소입니다.
//
// 파라미터로는
// 1. 데이터 값.
// 2. 데이터 Text Style
//
//

import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';

class InnerBox extends StatelessWidget {
  const InnerBox({
    super.key,
    required this.text,
    required this.style,
  });

  final String? text;
  final TextStyle? style;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 485.w,
      constraints: BoxConstraints(minHeight: 72.h),
      padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 30),
      decoration: BoxDecoration(
        border: Border.all(
          color: Colors.grey,
          width: 0.25,
        ),
      ),
      child: Text(text ?? '', style: style),
    );
  }
}
