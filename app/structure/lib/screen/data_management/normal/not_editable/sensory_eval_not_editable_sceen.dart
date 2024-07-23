//
//
// 관능 평가 페이지(수정 불가!) : Normal
//
//
//

import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/custom_app_bar.dart';
import 'package:structure/components/image_card.dart';
import 'package:structure/components/part_eval.dart';
import 'package:structure/config/pallete.dart';
import 'package:structure/viewModel/data_management/normal/not_editable/sensoty_eval_not_editable_view_model.dart';

class SensoryEvalNotEditableScreen extends StatefulWidget {
  const SensoryEvalNotEditableScreen({
    super.key,
  });

  @override
  State<SensoryEvalNotEditableScreen> createState() =>
      _SensoryEvalNotEditableScreenState();
}

class _SensoryEvalNotEditableScreenState
    extends State<SensoryEvalNotEditableScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 5, vsync: this);
  }

  List<List<String>> text = [
    ['Mabling', '마블링 정도', '없음', '', '보통', '', '많음'],
    ['Color', '육색', '없음', '', '보통', '', '어둡고 진함'],
    ['Texture', '조직감', '흐물함', '', '보통', '', '단단함'],
    ['Surface Moisture', '표면육즙', '없음', '', '보통', '', '많음'],
    ['Overall', '종합기호도', '나쁨', '', '보통', '', '좋음'],
  ];

  @override
  Widget build(BuildContext context) {
    SensoryEvalNotEditableViewModel sensoryEvalNotEditableViewModel =
        context.watch<SensoryEvalNotEditableViewModel>();

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: const CustomAppBar(
        title: '원육 관능평가',
        backButton: true,
        closeButton: false,
      ),
      body: SingleChildScrollView(
        child: Center(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              ImageCard(imagePath: sensoryEvalNotEditableViewModel.meatImage),
              SizedBox(height: 60.h),

              // 관능평가 데이터
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  SizedBox(width: 70.w),
                  Icon(
                    Icons.check,
                    color: sensoryEvalNotEditableViewModel.marbling > 0
                        ? Palette.mainButtonColor
                        : Colors.transparent,
                  ),
                  const Spacer(),
                  Icon(
                    Icons.check,
                    color: sensoryEvalNotEditableViewModel.color > 0
                        ? Palette.mainButtonColor
                        : Colors.transparent,
                  ),
                  const Spacer(),
                  Icon(
                    Icons.check,
                    color: sensoryEvalNotEditableViewModel.texture > 0
                        ? Palette.mainButtonColor
                        : Colors.transparent,
                  ),
                  const Spacer(),
                  Icon(
                    Icons.check,
                    color: sensoryEvalNotEditableViewModel.surface > 0
                        ? Palette.mainButtonColor
                        : Colors.transparent,
                  ),
                  const Spacer(),
                  Icon(
                    Icons.check,
                    color: sensoryEvalNotEditableViewModel.overall > 0
                        ? Palette.mainButtonColor
                        : Colors.transparent,
                  ),
                  SizedBox(width: 70.w),
                ],
              ),
              Container(
                margin: EdgeInsets.only(left: 24.w, right: 24.w),
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
                  labelStyle: Palette.h5BoldGray,
                  unselectedLabelStyle: Palette.h5LightGrey,
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
                height: 350.h,
                child: TabBarView(
                  controller: _tabController,
                  children: [
                    // 마블링
                    Column(children: [
                      PartEval(
                        idx: 0,
                        selectedText: text[0],
                        value: sensoryEvalNotEditableViewModel.marbling,
                        onChanged: null,
                      ),
                      Container(
                        margin: EdgeInsets.only(top: 16.h),
                        width: 640.w,
                        height: 90.h,
                        decoration: BoxDecoration(
                          color: const Color(0xFF9F9F9F),
                          borderRadius: BorderRadius.circular(20.r),
                        ),
                        child: Center(
                          child: Text(
                              sensoryEvalNotEditableViewModel.marbling
                                  .toString(),
                              style: TextStyle(
                                  color: Colors.white,
                                  fontSize: 36.sp,
                                  fontWeight: FontWeight.w500)),
                        ),
                      ),
                    ]),
                    // 육색
                    Column(children: [
                      PartEval(
                        idx: 1,
                        selectedText: text[1],
                        value: sensoryEvalNotEditableViewModel.color,
                        onChanged: null,
                      ),
                      Container(
                        margin: EdgeInsets.only(top: 16.h),
                        width: 640.w,
                        height: 90.h,
                        decoration: BoxDecoration(
                          color: const Color(0xFF9F9F9F),
                          borderRadius: BorderRadius.circular(20.r),
                        ),
                        child: Center(
                          child: Text(
                              sensoryEvalNotEditableViewModel.color.toString(),
                              style: TextStyle(
                                  color: Colors.white,
                                  fontSize: 36.sp,
                                  fontWeight: FontWeight.w500)),
                        ),
                      ),
                    ]),
                    // 조직감
                    Column(children: [
                      PartEval(
                        idx: 2,
                        selectedText: text[2],
                        value: sensoryEvalNotEditableViewModel.texture,
                        onChanged: null,
                      ),
                      Container(
                        margin: EdgeInsets.only(top: 16.h),
                        width: 640.w,
                        height: 90.h,
                        decoration: BoxDecoration(
                          color: const Color(0xFF9F9F9F),
                          borderRadius: BorderRadius.circular(20.r),
                        ),
                        child: Center(
                          child: Text(
                              sensoryEvalNotEditableViewModel.texture
                                  .toString(),
                              style: TextStyle(
                                  color: Colors.white,
                                  fontSize: 36.sp,
                                  fontWeight: FontWeight.w500)),
                        ),
                      ),
                    ]),
                    // 육즙
                    Column(children: [
                      PartEval(
                        idx: 3,
                        selectedText: text[3],
                        value: sensoryEvalNotEditableViewModel.surface,
                        onChanged: null,
                      ),
                      Container(
                        margin: EdgeInsets.only(top: 16.h),
                        width: 640.w,
                        height: 90.h,
                        decoration: BoxDecoration(
                          color: const Color(0xFF9F9F9F),
                          borderRadius: BorderRadius.circular(20.r),
                        ),
                        child: Center(
                          child: Text(
                              sensoryEvalNotEditableViewModel.surface
                                  .toString(),
                              style: TextStyle(
                                  color: Colors.white,
                                  fontSize: 36.sp,
                                  fontWeight: FontWeight.w500)),
                        ),
                      ),
                    ]),
                    // 기호도
                    Column(children: [
                      PartEval(
                        idx: 4,
                        selectedText: text[4],
                        value: sensoryEvalNotEditableViewModel.overall,
                        onChanged: null,
                      ),
                      Container(
                        margin: EdgeInsets.only(top: 16.h),
                        width: 640.w,
                        height: 90.h,
                        decoration: BoxDecoration(
                          color: const Color(0xFF9F9F9F),
                          borderRadius: BorderRadius.circular(20.r),
                        ),
                        child: Center(
                          child: Text(
                              sensoryEvalNotEditableViewModel.overall
                                  .toString(),
                              style: TextStyle(
                                  color: Colors.white,
                                  fontSize: 36.sp,
                                  fontWeight: FontWeight.w500)),
                        ),
                      ),
                    ]),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
