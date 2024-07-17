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
import 'package:structure/components/loading_screen.dart';
import 'package:structure/components/part_eval.dart';
import 'package:structure/config/pallete.dart';
import 'package:structure/viewModel/data_management/normal/not_editable/freshmeat_eval_not_editable_view_model.dart';

class FreshMeatEvalNotEditableScreen extends StatefulWidget {
  const FreshMeatEvalNotEditableScreen({
    super.key,
  });

  @override
  State<FreshMeatEvalNotEditableScreen> createState() =>
      _FreshMeatEvalNotEditableScreenState();
}

class _FreshMeatEvalNotEditableScreenState
    extends State<FreshMeatEvalNotEditableScreen>
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
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: const CustomAppBar(
        title: '신선육 관능평가',
        backButton: true,
        closeButton: false,
      ),
      body: SingleChildScrollView(
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
                  child: Image.network(
                    context.read<FreshMeatEvalNotEditableViewModel>().meatImage,
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

                    // 이미지 불러오기 에러
                    errorBuilder: (BuildContext context, Object error,
                        StackTrace? stackTrace) {
                      return const Icon(Icons.error);
                    },

                    fit: BoxFit.cover,
                  ),
                ),
              ),
              SizedBox(height: 30.h),

              // 관능평가 데이터
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  SizedBox(width: 70.w),
                  Icon(
                    Icons.check,
                    color: context
                                .watch<FreshMeatEvalNotEditableViewModel>()
                                .marbling >
                            0
                        ? Palette.mainButtonColor
                        : Colors.transparent,
                  ),
                  const Spacer(),
                  Icon(
                    Icons.check,
                    color: context
                                .watch<FreshMeatEvalNotEditableViewModel>()
                                .color >
                            0
                        ? Palette.mainButtonColor
                        : Colors.transparent,
                  ),
                  const Spacer(),
                  Icon(
                    Icons.check,
                    color: context
                                .watch<FreshMeatEvalNotEditableViewModel>()
                                .texture >
                            0
                        ? Palette.mainButtonColor
                        : Colors.transparent,
                  ),
                  const Spacer(),
                  Icon(
                    Icons.check,
                    color: context
                                .watch<FreshMeatEvalNotEditableViewModel>()
                                .surface >
                            0
                        ? Palette.mainButtonColor
                        : Colors.transparent,
                  ),
                  const Spacer(),
                  Icon(
                    Icons.check,
                    color: context
                                .watch<FreshMeatEvalNotEditableViewModel>()
                                .overall >
                            0
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
                child: Consumer<FreshMeatEvalNotEditableViewModel>(
                  builder: (context, viewModel, child) => TabBarView(
                    controller: _tabController,
                    children: [
                      // 마블링
                      Column(children: [
                        PartEval(
                          idx: 0,
                          selectedText: text[0],
                          value: viewModel.marbling,
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
                            child: Text(viewModel.marbling.toString(),
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
                          value: viewModel.color,
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
                            child: Text(viewModel.color.toString(),
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
                          value: viewModel.texture,
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
                            child: Text(viewModel.texture.toString(),
                                style: TextStyle(
                                    color: Colors.white,
                                    fontSize: 36.sp,
                                    fontWeight: FontWeight.w500)),
                          ),
                        ),
                        // Text(viewModel.texture.toString(),
                        //     style: Palette.dropDownTitleStyle)
                      ]),
                      // 육즙
                      Column(children: [
                        PartEval(
                          idx: 3,
                          selectedText: text[3],
                          value: viewModel.surface,
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
                            child: Text(viewModel.surface.toString(),
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
                          value: viewModel.overall,
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
                            child: Text(viewModel.overall.toString(),
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
              ),
            ],
          ),
        ),
      ),
    );
  }
}
