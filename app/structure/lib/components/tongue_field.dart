import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';

class TongueFiled extends StatelessWidget {
  final String mainText;
  final String subText;
  final TextEditingController controller;
  @override
  const TongueFiled({
    super.key,
    required this.mainText,
    required this.subText,
    required this.controller,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 42.w),
      child: Column(
        children: [
          Row(children: [
            Text(
              mainText,
              style: TextStyle(
                fontSize: 30.sp,
                fontWeight: FontWeight.w600,
              ),
            ),
            SizedBox(width: 10.w),
            Text(
              subText,
              style: TextStyle(
                fontSize: 30.sp,
                fontWeight: FontWeight.w400,
                color: const Color.fromARGB(255, 61, 57, 57),
              ),
            ),
          ]),
          SizedBox(
            width: 640.w,
            height: 88.h,
            child: TextField(
              decoration: InputDecoration(
                filled: true,
                fillColor: Colors.grey[200],
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8.0),
                  borderSide: BorderSide.none,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
