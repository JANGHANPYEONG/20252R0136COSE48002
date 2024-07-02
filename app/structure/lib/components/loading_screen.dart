import 'package:flutter/material.dart';
import 'package:structure/config/pallete.dart';

class LoadingScreen extends StatelessWidget {
  const LoadingScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const CircularProgressIndicator(
      color: Palette.loadingIcon,
    );
  }
}
