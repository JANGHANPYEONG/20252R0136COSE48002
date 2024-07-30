//
//
// 관능평가 페이지(View)
//
//

import 'dart:io';

import 'package:dotted_border/dotted_border.dart';
import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/custom_app_bar.dart';
import 'package:structure/components/loading_screen.dart';
import 'package:structure/components/main_button.dart';
import 'package:structure/components/part_eval.dart';
import 'package:structure/config/pallete.dart';
import 'package:structure/viewModel/meat_registration/insertion_sensory_eval_view_model.dart';

class SensoryEvalScreen extends StatefulWidget {
  const SensoryEvalScreen({super.key});

  @override
  State<SensoryEvalScreen> createState() => _SensoryEvalScreenState();
}

class _SensoryEvalScreenState extends State<SensoryEvalScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 5, vsync: this);
  }

  // 신선육 관능평가 label
  List<List<String>> text = [
    ['Mabling', '마블링 정도', '없음', '', '보통', '', '많음'],
    ['Color', '육색', '없음', '', '보통', '', '어둡고 진함'],
    ['Texture', '조직감', '흐물함', '', '보통', '', '단단함'],
    ['Surface Moisture', '표면육즙', '없음', '', '보통', '', '많음'],
    ['Overall', '종합기호도', '나쁨', '', '보통', '', '좋음'],
  ];

  @override
  Widget build(BuildContext context) {
    InsertionSensoryEvalViewModel freshMeatEvalViewModel =
        context.watch<InsertionSensoryEvalViewModel>();
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: CustomAppBar(
        title: freshMeatEvalViewModel.title,
        backButton: true,
        closeButton: false,
        backButtonOnPressed: freshMeatEvalViewModel.backBtnPressed(context),
      ),
      body: Stack(
        children: [
          SingleChildScrollView(
            child: Center(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  // SizedBox(height: 40.h),
                  ClipRRect(
                    borderRadius: BorderRadius.circular(20.0),
                    child: SizedBox(
                      width: 640.w,
                      height: 640.w,
                      // 관능평가를 위한 이미지 할당.
                      child: freshMeatEvalViewModel.meatImage != ''
                          ? freshMeatEvalViewModel.meatImage.contains('http')
                              ? Image.network(
                                  freshMeatEvalViewModel.meatImage,
                                  loadingBuilder: (BuildContext context,
                                      Widget child,
                                      ImageChunkEvent? loadingProgress) {
                                    if (loadingProgress == null) {
                                      return child;
                                    } else {
                                      return LoadingScreen(
                                        value: loadingProgress
                                                    .expectedTotalBytes !=
                                                null
                                            ? loadingProgress
                                                    .cumulativeBytesLoaded /
                                                (loadingProgress
                                                        .expectedTotalBytes ??
                                                    1)
                                            : null,
                                      );
                                    }
                                  },
                                  // 에러 정의
                                  errorBuilder: (BuildContext context,
                                      Object error, StackTrace? stackTrace) {
                                    return const Icon(Icons.error);
                                  },
                                  fit: BoxFit.cover,
                                )
                              : Image.file(
                                  File(freshMeatEvalViewModel.meatImage),
                                  fit: BoxFit.cover,
                                )
                          : InkWell(
                              child: DottedBorder(
                                radius: Radius.circular(20.r),
                                borderType: BorderType.RRect,
                                color: Palette.imageErrorColor,
                                strokeWidth: 2.sp,
                                dashPattern: [10.w, 10.w],
                                child: Column(
                                  children: [
                                    SizedBox(
                                      width: 640.w,
                                      height: 503.h,
                                      child: const Icon(
                                        Icons.error_outline,
                                        color: Palette.imageErrorColor,
                                        size: 50,
                                      ),
                                    ),
                                    const SizedBox(
                                      child: Text(
                                        '이미지 로드에 실패하였습니다',
                                        style: TextStyle(
                                            color: Palette.imageErrorColor),
                                      ),
                                    )
                                  ],
                                ),
                              ),
                            ),
                    ),
                  ),
                  SizedBox(height: 30.h),

                  // 관능평가 데이터가 입력 되었는지 체크.
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      SizedBox(width: 70.w),
                      Icon(
                        Icons.check,
                        color: context
                                    .watch<InsertionSensoryEvalViewModel>()
                                    .marbling >
                                0
                            ? Palette.meatRegiBtnBg
                            : Colors.transparent,
                      ),
                      const Spacer(),
                      Icon(
                        Icons.check,
                        color: freshMeatEvalViewModel.color > 0
                            ? Palette.meatRegiBtnBg
                            : Colors.transparent,
                      ),
                      const Spacer(),
                      Icon(
                        Icons.check,
                        color: freshMeatEvalViewModel.texture > 0
                            ? Palette.meatRegiBtnBg
                            : Colors.transparent,
                      ),
                      const Spacer(),
                      Icon(
                        Icons.check,
                        color: freshMeatEvalViewModel.surfaceMoisture > 0
                            ? Palette.meatRegiBtnBg
                            : Colors.transparent,
                      ),
                      const Spacer(),
                      Icon(
                        Icons.check,
                        color: freshMeatEvalViewModel.overall > 0
                            ? Palette.meatRegiBtnBg
                            : Colors.transparent,
                      ),
                      SizedBox(width: 70.w),
                    ],
                  ),
                  Container(
                    margin: EdgeInsets.only(left: 24.w, right: 24.w),
                    // tab을 이용하여 관능평가 항목을 구분.
                    child: TabBar(
                      controller: _tabController,
                      tabs: const [
                        Tab(child: Text('마블링')),
                        Tab(child: Text('육색')),
                        Tab(child: Text('조직감')),
                        Tab(child: Text('육즙')),
                        Tab(child: Text('기호도')),
                      ],
                      labelColor: Palette.dataMngBtndBg,
                      labelStyle: Palette.h5Bold,
                      unselectedLabelStyle: Palette.h5,
                      indicator: ShapeDecoration(
                        shape: Border(
                          bottom: BorderSide(
                            color: Colors.black,
                            width: 3.0.sp,
                          ),
                        ),
                      ),
                    ),
                  ),

                  Container(
                    margin: EdgeInsets.only(top: 10.h),
                    height: 250.h,
                    child: Consumer<InsertionSensoryEvalViewModel>(
                      // 'PartEval' 컴포넌트를 이용하여 관능평가 항목을 정의.
                      builder: (context, viewModel, child) => TabBarView(
                        controller: _tabController,
                        children: [
                          // 마블링
                          Center(
                            child: PartEval(
                              idx: 0,
                              selectedText: text[0],
                              value: viewModel.marbling,
                              onChanged: (value) =>
                                  viewModel.onChangedMarbling(value),
                            ),
                          ),

                          // 육색
                          Center(
                            child: PartEval(
                              idx: 1,
                              selectedText: text[1],
                              value: viewModel.color,
                              onChanged: (value) =>
                                  viewModel.onChangedColor(value),
                            ),
                          ),

                          // 조직감
                          Center(
                            child: PartEval(
                              idx: 2,
                              selectedText: text[2],
                              value: viewModel.texture,
                              onChanged: // 이게 sliding part
                                  (value) => viewModel.onChangedTexture(value),
                            ),
                          ),

                          // 육즙
                          Center(
                            child: PartEval(
                              idx: 3,
                              selectedText: text[3],
                              value: viewModel.surfaceMoisture,
                              onChanged: (value) =>
                                  viewModel.onChangedSurface(value),
                            ),
                          ),

                          // 기호도
                          Center(
                            child: PartEval(
                              idx: 4,
                              selectedText: text[4],
                              value: viewModel.overall,
                              onChanged: (value) =>
                                  viewModel.onChangedOverall(value),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),

                  // 데이터 저장 버튼
                  Container(
                    margin: EdgeInsets.only(bottom: 10.h),
                    child: MainButton(
                      onPressed: () async =>
                          freshMeatEvalViewModel.saveMeatData(context),
                      text: freshMeatEvalViewModel.saveBtnText(),
                      width: 658.w,
                      height: 104.h,
                      mode: 1,
                    ),
                  ),
                ],
              ),
            ),
          ),
          freshMeatEvalViewModel.isLoading
              ? const Center(child: LoadingScreen())
              : Container()
        ],
      ),
    );
  }
}
