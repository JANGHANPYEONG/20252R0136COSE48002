import 'dart:io';

import 'package:dotted_border/dotted_border.dart';
import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:structure/components/loading_screen.dart';
import 'package:structure/config/pallete.dart';

class ImageCard extends StatelessWidget {
  final String? imagePath;

  const ImageCard({
    super.key,
    required this.imagePath,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 40.w),
      width: 640.w,
      height: 640.w,
      child: ClipRRect(
        borderRadius: BorderRadius.circular(20.r),
        child: imagePath != null && imagePath!.contains('http')
            // s3에 업로드 된 이미지 (수정)
            ? Image.network(
                imagePath!,
                loadingBuilder: (BuildContext context, Widget child,
                    ImageChunkEvent? loadingProgress) {
                  if (loadingProgress == null) {
                    return child;
                  } else {
                    return const Center(child: LoadingScreen());
                  }
                },
                errorBuilder: (BuildContext context, Object error,
                    StackTrace? stackTrace) {
                  return const ImageError(isError: true);
                },
                fit: BoxFit.cover,
              )

            // 이미지 촬영 중 임시저장 된 사진
            : imagePath != null && imagePath!.isNotEmpty
                ? Image.file(File(imagePath!), fit: BoxFit.cover)
                : const ImageError(isError: false),
      ),
    );
  }
}

class ImageError extends StatelessWidget {
  final bool isError;
  const ImageError({super.key, required this.isError});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 640.w,
      height: 640.w,
      child: DottedBorder(
        radius: Radius.circular(20.r),
        borderType: BorderType.RRect,
        color: Pallete.imageErrorColor,
        strokeWidth: 2.sp,
        dashPattern: [12.w, 12.w],
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Center(
              child: Icon(
                Icons.error_outline,
                color: Pallete.imageErrorColor,
                size: 48,
              ),
            ),
            SizedBox(height: 16.h),
            Text(
              isError ? '이미지 로드에 실패하였습니다' : '이미지가 존재하지 않습니다',
              style: const TextStyle(color: Pallete.imageErrorColor),
            ),
          ],
        ),
      ),
    );
  }
}
