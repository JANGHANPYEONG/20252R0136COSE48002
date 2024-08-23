import 'package:flutter/material.dart';
import 'package:structure/config/palette.dart';

class DataTitle extends StatelessWidget {
  const DataTitle({super.key, required this.korText, required this.engText});

  final String korText;
  final String engText;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.start,
      children: [
        Text(
          '$engText ',
          textAlign: TextAlign.left,
          style: Palette.h4,
        ),
        Text(
          korText,
          textAlign: TextAlign.left,
          style: Palette.h4RegularOnSecondary,
        ),
      ],
    );
  }
}
