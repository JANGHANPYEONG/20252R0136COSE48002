import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';

class CameraGuide extends StatelessWidget {
  final Color color;

  const CameraGuide({super.key, required this.color});

  @override
  Widget build(BuildContext context) {
    return CustomPaint(
      painter: CameraOverlayPainter(color: color),
    );
  }
}

class CameraOverlayPainter extends CustomPainter {
  final Color color;

  CameraOverlayPainter({required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = 10.w;

    double length = 80.w;

    // 왼쪽 상단
    canvas.drawArc(
        Rect.fromCenter(
            center: const Offset(0, 0), width: length, height: length),
        1 * 3.14,
        0.5 * 3.14,
        false,
        paint);

    // 우측 상단
    canvas.drawArc(
        Rect.fromCenter(
            center: Offset(size.width, 0), width: length, height: length),
        1.5 * 3.14,
        0.5 * 3.14,
        false,
        paint);

    // 좌측 하단
    canvas.drawArc(
        Rect.fromCenter(
            center: Offset(0, size.width), width: length, height: length),
        2.5 * 3.14,
        0.5 * 3.14,
        false,
        paint);

    // 우측 하단
    canvas.drawArc(
        Rect.fromCenter(
            center: Offset(size.width, size.width),
            width: length,
            height: length),
        2 * 3.14,
        0.5 * 3.14,
        false,
        paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) {
    return false;
  }
}
