import 'package:flutter/material.dart';
import 'package:structure/config/pallete.dart';

class CustomTextButton extends StatelessWidget {
  final String title;
  final VoidCallback? onPressed;

  const CustomTextButton({super.key, required this.title, this.onPressed});

  @override
  Widget build(BuildContext context) {
    return TextButton(
      onPressed: onPressed,
      child: Text(
        title,
        style: Palette.customTextBtnStyle,
      ),
    );
  }
}
