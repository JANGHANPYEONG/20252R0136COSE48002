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
import 'package:structure/config/palette.dart';
import 'package:structure/viewModel/data_management/normal/not_editable/sensory_eval_not_editable_view_model.dart';

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
    _tabController.addListener(() => context
        .read<SensoryEvalNotEditableViewModel>()
        .updateDataText(_tabController.index));
  }

  @override
  Widget build(BuildContext context) {
    SensoryEvalNotEditableViewModel sensoryEvalNotEditableViewModel =
        context.watch<SensoryEvalNotEditableViewModel>();

    return Scaffold(
      appBar: const CustomAppBar(title: '원육 관능평가'),
      body: SingleChildScrollView(
        child: Container(
          margin: EdgeInsets.symmetric(horizontal: 40.w),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              SizedBox(height: 24.h),

              // 이미지
              ImageCard(imagePath: sensoryEvalNotEditableViewModel.meatImage),
              SizedBox(height: 32.h),

              // 관능평가 데이터
              // 관능평가 레이블 탭
              TabBar(
                controller: _tabController,
                tabs: const [
                  Tab(child: Text('마블링')),
                  Tab(child: Text('육색')),
                  Tab(child: Text('조직감')),
                  Tab(child: Text('육즙')),
                  Tab(child: Text('기호도')),
                ],
                labelColor: Colors.black,
                labelStyle: Palette.h5SemiBold,
                labelPadding: EdgeInsets.zero,
                unselectedLabelStyle: Palette.h5OnSecondary,
                indicatorSize: TabBarIndicatorSize.tab,
                indicator: UnderlineTabIndicator(
                  borderSide: BorderSide(width: 4.w),
                ),
              ),

              SizedBox(
                height: 248.h,
                child: TabBarView(
                  controller: _tabController,
                  children: [
                    // 마블링
                    PartEval(
                      idx: 0,
                      selectedText: sensoryEvalNotEditableViewModel.text[0],
                      value: sensoryEvalNotEditableViewModel.marbling,
                      onChanged: null,
                    ),

                    // 육색
                    PartEval(
                      idx: 1,
                      selectedText: sensoryEvalNotEditableViewModel.text[1],
                      value: sensoryEvalNotEditableViewModel.color,
                      onChanged: null,
                    ),

                    // 조직감
                    PartEval(
                      idx: 2,
                      selectedText: sensoryEvalNotEditableViewModel.text[2],
                      value: sensoryEvalNotEditableViewModel.texture,
                      onChanged: null,
                    ),

                    // 육즙
                    PartEval(
                      idx: 3,
                      selectedText: sensoryEvalNotEditableViewModel.text[3],
                      value: sensoryEvalNotEditableViewModel.surface,
                      onChanged: null,
                    ),

                    // 기호도
                    PartEval(
                      idx: 4,
                      selectedText: sensoryEvalNotEditableViewModel.text[4],
                      value: sensoryEvalNotEditableViewModel.overall,
                      onChanged: null,
                    ),
                  ],
                ),
              ),
              SizedBox(height: 64.h),

              // 데이터 값 표시
              Container(
                margin: EdgeInsets.only(bottom: 40.h),
                width: double.infinity,
                height: 96.h,
                decoration: BoxDecoration(
                  color: Palette.onSecondary,
                  borderRadius: BorderRadius.circular(20.r),
                ),
                child: Center(
                  child: Text(
                    sensoryEvalNotEditableViewModel.dataText,
                    style: Palette.h3Regular.copyWith(color: Colors.white),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
