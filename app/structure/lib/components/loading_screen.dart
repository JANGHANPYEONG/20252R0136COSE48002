import 'package:flutter/material.dart';
import 'package:structure/config/pallete.dart';

class LoadingScreen extends StatelessWidget {
  final double? value;
  const LoadingScreen({super.key, this.value});

  @override
  Widget build(BuildContext context) {
    return CircularProgressIndicator(
      color: Pallete.loadingIcon,
      value: value,
    );
  }
}
