import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';

class DataTitle extends StatelessWidget {
  const DataTitle({super.key, required this.korText, required this.engText});

  final String korText;
  final String engText;

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 40.w),
      alignment: Alignment.centerLeft,
      child: Row(
        children: [
          Text(
            '$engText ',
            textAlign: TextAlign.left,
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
          Text(
            korText,
            textAlign: TextAlign.left,
            style: const TextStyle(color: Colors.grey),
          ),
        ],
      ),
    );
  }
}
