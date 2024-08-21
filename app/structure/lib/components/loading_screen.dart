import 'package:flutter/material.dart';
import 'package:structure/config/palette.dart';

class LoadingScreen extends StatelessWidget {
  final double? value;
  const LoadingScreen({super.key, this.value});

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        const ModalBarrier(dismissible: false),
        Center(
          child: CircularProgressIndicator(
            color: Palette.primary,
            value: value,
          ),
        ),
      ],
    );
  }
}
