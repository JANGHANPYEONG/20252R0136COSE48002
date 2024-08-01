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
      backgroundColor: Colors.white,
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
            child: Center(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  // 이미지
                  ImageCard(imagePath: insertionSeosnryEvalViewModel.meatImage),
                  SizedBox(height: 64.h),

                  // 관능평가 레이블 탭
                  Container(
                    margin: EdgeInsets.symmetric(horizontal: 40.w),
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
                      labelColor: Pallete.dataMngBtndBg,
                      labelStyle: Pallete.h5Bold,
                      unselectedLabelStyle: Pallete.h5,
                      indicator: ShapeDecoration(
                        shape: Border(
                          bottom: BorderSide(
                            color: Colors.black,
                            width: 4.w,
                          ),
                        ),
                      ),
                    ),
                  ),

                  // PartEval 탭
                  SizedBox(
                    height: 250.h,
                    child: TabBarView(
                      controller: _tabController,
                      children: [
                        // 마블링
                        Center(
                          child: PartEval(
                            idx: 0,
                            selectedText: text[0],
                            value: insertionSeosnryEvalViewModel.marbling,
                            onChanged: (value) => insertionSeosnryEvalViewModel
                                .onChangedMarbling(value),
                          ),
                        ),

                        // 육색
                        Center(
                          child: PartEval(
                            idx: 1,
                            selectedText: text[1],
                            value: insertionSeosnryEvalViewModel.color,
                            onChanged: (value) => insertionSeosnryEvalViewModel
                                .onChangedColor(value),
                          ),
                        ),

                        // 조직감
                        Center(
                          child: PartEval(
                            idx: 2,
                            selectedText: text[2],
                            value: insertionSeosnryEvalViewModel.texture,
                            onChanged: // 이게 sliding part
                                (value) => insertionSeosnryEvalViewModel
                                    .onChangedTexture(value),
                          ),
                        ),

                        // 육즙
                        Center(
                          child: PartEval(
                            idx: 3,
                            selectedText: text[3],
                            value:
                                insertionSeosnryEvalViewModel.surfaceMoisture,
                            onChanged: (value) => insertionSeosnryEvalViewModel
                                .onChangedSurface(value),
                          ),
                        ),

                        // 기호도
                        Center(
                          child: PartEval(
                            idx: 4,
                            selectedText: text[4],
                            value: insertionSeosnryEvalViewModel.overall,
                            onChanged: (value) => insertionSeosnryEvalViewModel
                                .onChangedOverall(value),
                          ),
                        ),
                      ],
                    ),
                  ),
                  SizedBox(height: 16.h),

                  // 데이터 저장 버튼
                  Container(
                    margin: EdgeInsets.fromLTRB(40.w, 0, 40.w, 40.w),
                    child: MainButton(
                      onPressed: () async =>
                          insertionSeosnryEvalViewModel.saveMeatData(context),
                      text: insertionSeosnryEvalViewModel.saveBtnText(),
                      width: double.infinity,
                      height: 96.h,
                      mode: 1,
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
