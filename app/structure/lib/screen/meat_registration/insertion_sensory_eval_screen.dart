//
//
// 관능평가 페이지(View)
//
//

import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/custom_app_bar.dart';
import 'package:structure/components/image_card.dart';
import 'package:structure/components/loading_screen.dart';
import 'package:structure/components/main_button.dart';
import 'package:structure/components/part_eval.dart';
import 'package:structure/config/palette.dart';
import 'package:structure/viewModel/meat_registration/insertion_sensory_eval_view_model.dart';

class InsertionSensoryEvalScreen extends StatefulWidget {
  const InsertionSensoryEvalScreen({super.key});

  @override
  State<InsertionSensoryEvalScreen> createState() =>
      _InsertionSensoryEvalScreenState();
}

class _InsertionSensoryEvalScreenState extends State<InsertionSensoryEvalScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 5, vsync: this);
  }

  // 원육 관능평가 label
  List<List<String>> text = [
    ['Mabling', '마블링 정도', '없음', '', '보통', '', '많음'],
    ['Color', '육색', '없음', '', '보통', '', '어둡고 진함'],
    ['Texture', '조직감', '흐물함', '', '보통', '', '단단함'],
    ['Surface Moisture', '표면육즙', '없음', '', '보통', '', '많음'],
    ['Overall', '종합기호도', '나쁨', '', '보통', '', '좋음'],
  ];

  @override
  Widget build(BuildContext context) {
    InsertionSensoryEvalViewModel insertionSeosnryEvalViewModel =
        context.watch<InsertionSensoryEvalViewModel>();

    return Scaffold(
      appBar: CustomAppBar(
        title: insertionSeosnryEvalViewModel.title,
        backButton: true,
        closeButton: false,
        backButtonOnPressed:
            insertionSeosnryEvalViewModel.backBtnPressed(context),
      ),
      body: Stack(
        children: [
          SingleChildScrollView(
            child: Container(
              margin: EdgeInsets.symmetric(horizontal: 40.w),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  SizedBox(height: 24.h),

                  // 이미지
                  ImageCard(imagePath: insertionSeosnryEvalViewModel.meatImage),
                  SizedBox(height: 32.h),

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
                    unselectedLabelStyle: Palette.h5,
                    indicatorSize: TabBarIndicatorSize.tab,
                    indicator: UnderlineTabIndicator(
                      borderSide: BorderSide(width: 4.w),
                    ),
                  ),

                  // PartEval 탭
                  SizedBox(
                    height: 248.h,
                    child: TabBarView(
                      controller: _tabController,
                      children: [
                        // 마블링
                        PartEval(
                          idx: 0,
                          selectedText: text[0],
                          value: insertionSeosnryEvalViewModel.marbling,
                          onChanged: (value) => insertionSeosnryEvalViewModel
                              .onChangedMarbling(value),
                        ),

                        // 육색
                        PartEval(
                          idx: 1,
                          selectedText: text[1],
                          value: insertionSeosnryEvalViewModel.color,
                          onChanged: (value) => insertionSeosnryEvalViewModel
                              .onChangedColor(value),
                        ),

                        // 조직감
                        PartEval(
                          idx: 2,
                          selectedText: text[2],
                          value: insertionSeosnryEvalViewModel.texture,
                          onChanged: // 이게 sliding part
                              (value) => insertionSeosnryEvalViewModel
                                  .onChangedTexture(value),
                        ),

                        // 육즙
                        PartEval(
                          idx: 3,
                          selectedText: text[3],
                          value: insertionSeosnryEvalViewModel.surfaceMoisture,
                          onChanged: (value) => insertionSeosnryEvalViewModel
                              .onChangedSurface(value),
                        ),

                        // 기호도
                        PartEval(
                          idx: 4,
                          selectedText: text[4],
                          value: insertionSeosnryEvalViewModel.overall,
                          onChanged: (value) => insertionSeosnryEvalViewModel
                              .onChangedOverall(value),
                        ),
                      ],
                    ),
                  ),
                  SizedBox(height: 64.h),

                  // 데이터 저장 버튼
                  Container(
                    margin: EdgeInsets.only(bottom: 40.h),
                    child: MainButton(
                      width: double.infinity,
                      height: 96.h,
                      text: insertionSeosnryEvalViewModel.saveBtnText(),
                      onPressed: () async =>
                          insertionSeosnryEvalViewModel.saveMeatData(context),
                    ),
                  ),
                ],
              ),
            ),
          ),
          insertionSeosnryEvalViewModel.isLoading
              ? const Center(child: LoadingScreen())
              : Container()
        ],
      ),
    );
  }
}
