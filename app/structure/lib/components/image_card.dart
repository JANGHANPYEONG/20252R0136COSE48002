import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:structure/components/loading_screen.dart';

class ImageCard extends StatelessWidget {
  final String imagePath;

  const ImageCard({
    super.key,
    required this.imagePath,
  });

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(20.r),
      child: SizedBox(
        width: 640.w,
        height: 640.w,

        // 이미지 할당
        child:
            // imagePath !=
            //             null &&
            imagePath.contains('http')
                // s3에 업로드 된 이미지 (수정)
                ? Image.network(
                    imagePath,
                    loadingBuilder: (BuildContext context, Widget child,
                        ImageChunkEvent? loadingProgress) {
                      if (loadingProgress == null) {
                        return child;
                      } else {
                        return LoadingScreen(
                          value: loadingProgress.expectedTotalBytes != null
                              ? loadingProgress.cumulativeBytesLoaded /
                                  (loadingProgress.expectedTotalBytes ?? 1)
                              : null,
                        );
                      }
                    },
                    errorBuilder: (BuildContext context, Object error,
                        StackTrace? stackTrace) {
                      return const Icon(Icons.error);
                    },
                    fit: BoxFit.cover,
                  )
                // 이미지 촬영 중 임시저장 된 사진
                : Image.file(
                    File(imagePath),
                    fit: BoxFit.cover,
                  ),
      ),
    );
  }
}
