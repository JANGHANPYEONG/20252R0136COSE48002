import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/main_button.dart';
import 'package:structure/config/pallete.dart';
import 'package:structure/config/userfuls.dart';
import 'package:structure/viewModel/meat_registration/creation_management_num_view_model.dart.dart';

class CreationManagementNumScreen extends StatelessWidget {
  const CreationManagementNumScreen({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: Center(
        child: context.watch<CreationManagementNumViewModel>().isLoading
            ? const Text('관리번호 생성중')
            : Column(
                children: [
                  SizedBox(
                    height: 550.h,
                    child: Stack(
                      children: [
                        Center(
                          child: Transform.translate(
                            offset: Offset(0, 150.h),
                            child: Stack(
                              children: [
                                Positioned(
                                  left: 0.w,
                                  bottom: 0,
                                  child: const Icon(
                                    Icons.auto_awesome,
                                    color: Palette.starIcon,
                                  ),
                                ),
                                Icon(
                                  Icons.check_circle,
                                  size: 120.w,
                                  color: Palette.mainBtnAtvBg,
                                ),
                                const Positioned(
                                  right: 0,
                                  child: Icon(
                                    Icons.auto_awesome,
                                    color: Palette.starIcon,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                        Container(
                          margin: EdgeInsets.only(left: 46.w, top: 182.h),
                          child: Text('관리 번호가\n생성되었습니다!', style: Palette.h2),
                        ),
                        Positioned(
                          top: 182.h,
                          right: 46.w,
                          child: InkWell(
                            onTap: () async => await context
                                .read<CreationManagementNumViewModel>()
                                .printQr(),
                            child: Container(
                              width: 120.w,
                              height: 150.h,
                              decoration: BoxDecoration(
                                borderRadius: BorderRadius.circular(20.sp),
                                color: Palette.mainBtnAtvBg,
                              ),
                              child: Column(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Icon(
                                    Icons.print,
                                    size: 70.sp,
                                    color: Colors.white,
                                  ),
                                  Text(
                                    'QR코드\n인쇄',
                                    textAlign: TextAlign.center,
                                    style: Palette.h5White,
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                  Container(
                    width: 456.w,
                    height: 141.h,
                    alignment: Alignment.center,
                    decoration: BoxDecoration(
                      color: Palette.dataMngCardBg,
                      borderRadius: BorderRadius.circular(30.r),
                    ),
                    child: Text(
                      context
                          .read<CreationManagementNumViewModel>()
                          .managementNum,
                      textAlign: TextAlign.center,
                      style: Palette.h1,
                    ),
                  ),
                  SizedBox(
                    height: 35.h,
                  ),
                  Container(
                    width: 640.w,
                    height: 251.h,
                    padding:
                        EdgeInsets.symmetric(horizontal: 44.w, vertical: 55.h),
                    decoration: BoxDecoration(
                      border: Border.all(color: Palette.fieldBorder),
                      borderRadius: BorderRadius.circular(20.r),
                    ),
                    child: Column(children: [
                      Row(
                        children: [
                          Text(
                            '기본 정보',
                            style: Palette.h5Grey,
                          ),
                          const Spacer(),
                          ClipOval(
                            child: Image.file(
                              File(context
                                  .read<CreationManagementNumViewModel>()
                                  .meatModel
                                  .imagePath!),
                              width: 44.w,
                              height: 44.h,
                              fit: BoxFit.fill,
                            ),
                          ),
                          SizedBox(
                            width: 25.w,
                          ),
                          Text(
                            '${context.read<CreationManagementNumViewModel>().meatModel.speciesValue}•${context.read<CreationManagementNumViewModel>().meatModel.primalValue}•${context.read<CreationManagementNumViewModel>().meatModel.secondaryValue}',
                            style: Palette.h5,
                          )
                        ],
                      ),
                      const Spacer(),
                      Row(children: [
                        Text(
                          '이력번호',
                          style: Palette.h5Grey,
                        ),
                        const Spacer(),
                        Text(
                          "${context.read<CreationManagementNumViewModel>().meatModel.traceNum}",
                          style: Palette.h5,
                        )
                      ]),
                      const Spacer(),
                      Row(
                        children: [
                          Text(
                            '날짜',
                            style: Palette.h5Grey,
                          ),
                          const Spacer(),
                          Text(
                            Usefuls.parseDate(context
                                .read<CreationManagementNumViewModel>()
                                .meatModel
                                .createdAt),
                            style: Palette.h5,
                          )
                        ],
                      )
                    ]),
                  ),
                  const Spacer(),
                  Container(
                    margin: const EdgeInsets.only(bottom: 40),
                    child: MainButton(
                      onPressed: () => context
                          .read<CreationManagementNumViewModel>()
                          .clickedHomeButton(context),
                      text: '홈으로 이동',
                      width: 658.w,
                      height: 104.h,
                      mode: 1,
                    ),
                  ),
                ],
              ),
      ),
    );
  }
}
