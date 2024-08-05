import 'package:flutter/material.dart';

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
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        Text(
          korText,
          textAlign: TextAlign.left,
          style: const TextStyle(color: Colors.grey),
        ),
      ],
    );
  }
}
