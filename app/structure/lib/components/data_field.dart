import 'package:structure/config/pallete.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';

class DataField extends StatelessWidget {
  final String mainText;
  final String subText;
  final String? unit;
  final TextEditingController controller;
  final bool? isPercent;

  const DataField({
    super.key,
    required this.mainText,
    required this.subText,
    this.unit,
    required this.controller,
    this.isPercent,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      // width: double.infinity,
      // margin: EdgeInsets.fromLTRB(60.w, 0, 0, 112.h),
      margin: EdgeInsets.symmetric(horizontal: 42.w),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.start,
        children: [
          SizedBox(
            // width: 278.w,
            child: Row(
              children: [
                Text(
                  mainText,
                  style: TextStyle(
                    color: const Color(0xFF000000),
                    fontSize: 36.sp,
                  ),
                ),
                Text(
                  subText,
                  style: TextStyle(
                    color: Palette.greyTextColor,
                    fontSize: 30.sp,
                  ),
                ),
              ],
            ),
          ),
          Row(
            children: [
              SizedBox(
                width: 635.w,
                child: TextField(
                  decoration: InputDecoration(
                    filled: true,
                    fillColor: Colors.grey[200],
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8.0),
                      borderSide: BorderSide.none,
                    ),
                    suffixIcon: unit != null
                        ? Container(
                            width: 20.w, // 필요한 너비로 조정
                            height: 20.h,
                            alignment: Alignment.center, // 오른쪽 끝에 맞춤
                            child: Text(
                              unit!,
                              style: TextStyle(
                                color: const Color(0xFF686868),
                                fontSize: 30.sp,
                                fontStyle: FontStyle.normal,
                                fontWeight: FontWeight.w400,
                              ),
                            ),
                          )
                        : null,
                  ),
                  textAlign: TextAlign.center,
                  controller: controller,
                  inputFormatters: isPercent != null && isPercent == true
                      ? [
                          _PercentageInputFormatter(),
                        ]
                      : [
                          FilteringTextInputFormatter.allow(
                              RegExp(r'^-?\d{0,8}(\.\d{0,4})?')),
                        ],
                  keyboardType: TextInputType.number,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _PercentageInputFormatter extends TextInputFormatter {
  @override
  TextEditingValue formatEditUpdate(
      TextEditingValue oldValue, TextEditingValue newValue) {
    double parsedValue = double.tryParse(newValue.text) ?? 0.0;

    if (parsedValue < 0 || parsedValue > 100 || newValue.text.length > 7) {
      // 입력이 0부터 100 사이의 퍼센트 값이 아닌 경우, 입력을 무시합니다.
      return oldValue;
    }

    return newValue;
  }
}
