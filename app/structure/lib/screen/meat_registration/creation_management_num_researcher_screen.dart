import 'dart:io';
import 'package:flutter_spinkit/flutter_spinkit.dart';
import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/main_button.dart';
import 'package:structure/config/pallete.dart';
import 'package:structure/config/userfuls.dart';
import 'package:structure/viewModel/meat_registration/creation_management_num_researcher_view_model.dart';

class CreationManagementNumResearcherNumScreen extends StatelessWidget {
  const CreationManagementNumResearcherNumScreen({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: Container(
        child: context
                .watch<CreationManagementNumResearcherViewModel>()
                .isLoading
            ? Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Container(
                  margin: EdgeInsets.only(
                    left: 46.w,
                    top: 182.h,
                  ),
                  child: Text('관리 번호를\n생성 중 입니다.', style: Palette.h2),
                ),
                SizedBox(height: 80.h),
                const SpinKitThreeBounce(
                  color: Palette.mainBtnAtvBg,
                  size: 50.0,
                ),
                SizedBox(height: 90.h),
                Center(child: Image.asset('assets/images/print.png')),
              ])
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
                          .read<CreationManagementNumResearcherViewModel>()
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
                                  .read<
                                      CreationManagementNumResearcherViewModel>()
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
                            '${context.read<CreationManagementNumResearcherViewModel>().meatModel.speciesValue}•${context.read<CreationManagementNumResearcherViewModel>().meatModel.primalValue}•${context.read<CreationManagementNumResearcherViewModel>().meatModel.secondaryValue}',
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
                          "${context.read<CreationManagementNumResearcherViewModel>().meatModel.traceNum}",
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
                                .read<
                                    CreationManagementNumResearcherViewModel>()
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
                    margin: const EdgeInsets.only(bottom: 10),
                    child: MainButton(
                      onPressed: () async => await context
                          .read<CreationManagementNumResearcherViewModel>()
                          .printQr(),
                      text: 'QR코드 출력하기',
                      width: 658.w,
                      height: 104.h,
                      mode: 1,
                    ),
                  ),
                  Container(
                    margin: EdgeInsets.only(bottom: 10.h),
                    child: TextButton(
                      onPressed: () => context
                          .read<CreationManagementNumResearcherViewModel>()
                          .clickedHomeButton(context),
                      // onPressed: () async => context
                      //     .read<CreationManagementNumResearcherViewModel>()
                      //     .clickedAddData(context),
                      child: const Text(
                        '홈으로 이동하기',
                        style: TextStyle(
                          color: Colors.black,
                          decoration: TextDecoration.underline,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
      ),
    );
  }
}
